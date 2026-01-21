import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItemLabel, TableCell
import pandas as pd

from extractors.multiplier_detector import MultiplierDetector
from extractors.number_extractor import NumberExtractor
from models.dataclasses import *

class DoclingPDFAnalyzer:     
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.candidates: List[NumberCandidate] = []
        self.doc_converter = DocumentConverter()
        self.debug = False
        self.doc = None  

    def _detect_table_unit_context(self, df: pd.DataFrame, caption: Optional[str]) -> UnitContext:
        texts = [caption] if caption else []
        texts.extend([str(c) for c in df.columns if isinstance(c, str)])
        if not df.empty:
            texts.extend(df.iloc[0].astype(str).tolist())
        for text in texts:
            mult, source = MultiplierDetector.detect_multiplier(text)
            if mult > 1:
                return UnitContext(unit="USD", multiplier=mult, source=f"table context: {source}")
        return UnitContext(unit="UNKNOWN", multiplier=1.0, source="default")

    def _detect_column_unit_overrides(self, df: pd.DataFrame, table_ctx: UnitContext) -> Dict[int, UnitContext]:
        overrides = {}
        for col_idx, col_name in enumerate(df.columns):
            if not isinstance(col_name, str):
                continue
            mult, source = MultiplierDetector.detect_multiplier(col_name)
            if mult > 1 and mult != table_ctx.multiplier:
                overrides[col_idx] = UnitContext(unit="USD", multiplier=mult, source=f"column header: {col_name}")
        return overrides

    def _extract_from_text_element(self, item, text, element_type, page, level):
        element_mult, element_mult_source = MultiplierDetector.detect_multiplier(text)
        numbers = NumberExtractor.extract_numbers(text)
        for value, matched_text, start, end, has_suffix in numbers:
            context_start = max(0, start - 100)
            context_end = min(len(text), end + 100)
            context = text[context_start:context_end]
            if has_suffix:
                local_mult = 1.0
                local_source = "inline suffix"

            else:
                local_mult, local_source = MultiplierDetector.detect_multiplier(context, text[:200])
                if local_mult == 1.0 and element_mult > 1.0:
                    local_mult = element_mult
                    local_source = element_mult_source
            adjusted = abs(value * local_mult)
            candidate = NumberCandidate(
                raw_value=value,
                adjusted_value=adjusted,
                text=matched_text,
                context=context.strip(),
                page=page,
                position={'start': start, 'end': end, 'level': level},
                multiplier=local_mult,
                multiplier_source=local_source,
                confidence=self._calculate_confidence(value, local_mult, context, element_type, has_suffix),
                element_type=element_type
            )
            self.candidates.append(candidate)

    def _calculate_confidence(self, value: float, multiplier: float, context: str, element_type: str, has_suffix: bool = False) -> float:
        confidence = 0.6
        if has_suffix:
            confidence *= 1.2
        if element_type == "Table":
            confidence *= 1.15
        if value < 10 and multiplier > 1000 and not has_suffix:
            confidence *= 0.7
        if '%' in context or 'percent' in context.lower():
            confidence *= 0.5
        if 'per share' in context.lower() or 'per unit' in context.lower():
            confidence *= 0.6
        if 'footnote' in element_type.lower():
            confidence *= 0.3
        return min(confidence, 1.0)

    def _extract_with_semantic_chunking(self, doc):
        for item, level in doc.iterate_items():
            label = getattr(item, "label", None)
            text = getattr(item, "text", "")
            if not text:
                continue
            page = getattr(item, "page_no", None) or getattr(item, "page", None) or 1
            if label != DocItemLabel.TABLE:
                self._extract_from_text_element(item, text, str(label) if label else "Unknown", page, level)
        tables_info = self.get_tables_info()
        self._add_table_candidates(tables_info)

    def _add_table_candidates(self, tables_info: List[TableInfo]):
        for table in tables_info:
            for _, row in table.audit_df.iterrows():
                if row["raw_value"] is None:
                    continue
                candidate = NumberCandidate(
                    raw_value=row["raw_value"],
                    adjusted_value=abs(row["adjusted_value"]) if row["adjusted_value"] is not None else abs(row["raw_value"]),
                    text=row["raw_text"],
                    context=f"Table {table.table_number}, column '{row['column']}'",
                    page=row["page"],
                    position={"table": table.table_number, "row": row["row"], "column": row["column"]},
                    multiplier=row["multiplier"] or 1.0,
                    multiplier_source=row["source"] or "table",
                    confidence=0.9,
                    element_type="TABLE"
                )
                self.candidates.append(candidate)

    def extract_from_pdf(self) -> List[NumberCandidate]:
        result = self.doc_converter.convert(str(self.pdf_path))
        self.doc = result.document 
        self._extract_with_semantic_chunking(self.doc)
        return self.candidates

    def get_tables_info(self) -> List[TableInfo]:
        tables_info: List[TableInfo] = []
        docling_document = self.doc
        if not hasattr(docling_document, "tables") or not docling_document.tables:
            return tables_info
        for table_idx, table in enumerate(docling_document.tables, 1):
            try:
                df = table.export_to_dataframe(doc=docling_document)
                prov = getattr(table, "prov", [])
                page_no = next(
                    (p.page_no for p in getattr(table, "prov", []) if getattr(p, "page_no", None) is not None),
                    None,
                )

                caption_text = getattr(table, "caption_text", None)
                caption = caption_text if caption_text and not callable(caption_text) else None
                table_ctx = self._detect_table_unit_context(df, caption)
                column_overrides = self._detect_column_unit_overrides(df, table_ctx)
                normalized_df = df.copy()
                audit_rows: List[AuditRow] = []
                for row_idx, row in df.iterrows():
                    for col_idx, col_name in enumerate(df.columns):
                        raw_text = str(row[col_name])
                        raw_value = NumberExtractor.parse_number(raw_text)
                        if col_idx == 0:
                            audit_rows.append(AuditRow(
                                table=table_idx,
                                page=page_no,
                                row=row_idx,
                                column=col_name,
                                raw_text=raw_text,
                                raw_value=None,
                                adjusted_value=None,
                                unit=None,
                                multiplier=None,
                                source="label"
                            ))
                            continue
                        ctx = column_overrides.get(col_idx, table_ctx)
                        adjusted_value = raw_value * ctx.multiplier if raw_value is not None else None
                        normalized_df.at[row_idx, col_name] = adjusted_value if adjusted_value is not None else raw_text
                        audit_rows.append(AuditRow(
                            table=table_idx,
                            page=page_no,
                            row=row_idx,
                            column=col_name,
                            raw_text=raw_text,
                            raw_value=raw_value,
                            adjusted_value=adjusted_value,
                            unit=ctx.unit,
                            multiplier=ctx.multiplier,
                            source=ctx.source
                        ))
                audit_df = pd.DataFrame([asdict(row) for row in audit_rows])
                tables_info.append(TableInfo(
                    table_number=table_idx,
                    page=page_no,
                    caption=caption,
                    table_unit=table_ctx.unit,
                    table_multiplier=table_ctx.multiplier,
                    table_multiplier_source=table_ctx.source,
                    column_overrides={idx: asdict(ctx) for idx, ctx in column_overrides.items()},
                    original_df=df,
                    normalized_df=normalized_df,
                    audit_df=audit_df,
                    shape=df.shape,
                    is_empty=df.empty
                ))
            except Exception as e:
                print(f"Warning: Could not process table {table_idx}: {e}")
        return tables_info

    def rank_candidates(self, top_n: int = 20) -> List[NumberCandidate]:
        valid_candidates = [c for c in self.candidates if c.adjusted_value < 1e15 and c.element_type.lower() != "footnote"]
        ranked = sorted(valid_candidates, key=lambda x: (x.adjusted_value, x.confidence), reverse=True)
        return ranked[:top_n]

    def generate_report(self, top_n: int = 20) -> str:
        top_candidates = self.rank_candidates(top_n)
        report = [f"# PDF Number Analysis Report\n**Document:** {self.pdf_path.name}\n**Total numbers found:** {len(self.candidates)}\n\n## Top Numbers\n"]
        if not self.candidates:
            report.append("No numbers found.")
            return "\n".join(report)
        non_footnote_candidates = [
            c for c in self.candidates
            if c.raw_value is not None
            and c.element_type.lower() != "footnote"
        ]

        largest_raw = max(
            non_footnote_candidates,
            key=lambda x: abs(x.raw_value)
        )
        largest_adjusted = top_candidates[0]
        report.append(f"### Largest Raw Number: {largest_raw.raw_value:,.2f}\n- Page: {largest_raw.page}\n- Type: {largest_raw.element_type}\n- Text: `{largest_raw.text}`\n")
        report.append(f"### Largest Adjusted Number: {largest_adjusted.adjusted_value:,.2f}\n- Raw: {largest_adjusted.raw_value:,.2f}\n- Multiplier: {largest_adjusted.multiplier} ({largest_adjusted.multiplier_source})\n- Page: {largest_adjusted.page}\n- Type: {largest_adjusted.element_type}\n")
        report.append("\n### Top Candidates\n| Rank | Adjusted | Raw | Multiplier | Page | Type | Context |\n")
        for i, c in enumerate(top_candidates, 1):
            ctx = c.context[:80].replace('\n', ' ').replace('|', '/')
            report.append(f"| {i} | {c.adjusted_value:,.0f} | {c.raw_value:,.2f} | {c.multiplier:,.0f}x | {c.page} | {c.element_type} | {ctx}... |")
        return "\n".join(report)

    def save_results(self, output_dir: str = "results"):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        top_candidates = self.rank_candidates(50)
        with open(output_path / "top_candidates.json", 'w') as f:
            json.dump([c.to_dict() for c in top_candidates], f, indent=2)
        report = self.generate_report()
        with open(output_path / "analysis_report.md", 'w') as f:
            f.write(report)
        print(f"Results saved to {output_dir}/")

def main(
    pdf_path: str,
    top_n: int = 20,
    output_dir: str = "results",
    debug: bool = False,
    no_chunking: bool = False,
):
    analyzer = DoclingPDFAnalyzer(pdf_path)
    analyzer.debug = debug

    if no_chunking:
        analyzer.use_chunking = False  

    analyzer.extract_from_pdf()

    print("\n" + analyzer.generate_report(top_n))
    analyzer.save_results(output_dir)

    # if analyzer.candidates:
    #     top = analyzer.rank_candidates(1)[0]
    #     print(f"\nANSWER:")
    #     print(
    #         f"   Largest raw number: "
    #         f"{max(analyzer.candidates, key=lambda x: abs(x.raw_value)).raw_value:,.2f}"
    #     )
    #     print(f"   Largest adjusted number: {top.adjusted_value:,.2f}")
    #     print(f"   (from {top.raw_value:,.2f} × {top.multiplier:,.0f})")
    # else:
    #     print("\nNo numbers found in document")

    return analyzer


def cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze numeric values in a PDF using Docling"
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the PDF document to analyze",
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top numeric candidates to display (default: 20)",
    )

    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory to save extracted results (default: results)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--no-chunking",
        action="store_true",
        help="Disable Docling chunked retrieval",
    )

    args = parser.parse_args()

    main(
        pdf_path=args.pdf_path,
        top_n=args.top_n,
        output_dir=args.output_dir,
        debug=args.debug,
        no_chunking=args.no_chunking,
    )


if __name__ == "__main__":
    cli()
