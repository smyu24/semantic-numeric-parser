# PDF Number Extraction & Analysis System

## Problem:

Given an unidentified document, must parse through and Extract the largest number from a PDF document in two ways:

1. **Raw largest number** : The biggest numerical value as written
2. **Adjusted largest number** : Accounting for context like "in millions" or "in thousands"

## Why Docling Classic: focusing on high quality document understanding pipeline

Given a heterogenous layout, Docling enables us to be able to...

1. Make Semantic Groupings
2. Perform Content Extraction given Element Aware Processing, even in complex multimodal layouts
3. Give Structured Exporting (Going from PDF -> structured representations)
4. Confidence Scoring based on Context Clues + Multipliers (elem type + textual context)
5. Auditing via tracking trail of how number was found

built on gold standard of https://arxiv.org/pdf/2206.01062

### Key Components

```
DoclingPDFAnalyzer (Main orchestrator)
├── DocumentConverter (Docling's PDF processor)
├── DoclingChunkStore (Manages semantic chunks)
├── NumberExtractor (Finds and parses numbers)
├── MultiplierDetector (Detects scale factors)
└── NumberCandidate (Stores results with metadata)
```

## Tabular

tabulate, load then normalize

## Sample Console Output

```
# PDF Number Analysis Report
**Document:** FY25_Air_Force.pdf
**Total numbers found:** 8245

## Top Numbers

### Largest Raw Number: 9,000,000,000.00
- Page: 1
- Type: text
- Text: ` 9B`

### Largest Adjusted Number: 35,110,000,000.00
- Raw: 35,110.00
- Multiplier: 1000000.0 (table context: million)
- Page: 13
- Type: TABLE


### Top Candidates
| Rank | Adjusted | Raw | Multiplier | Page | Type | Context |

| 1 | 35,110,000,000 | 35,110.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 2 | 34,735,000,000 | 34,735.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 3 | 33,848,000,000 | 33,848.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 4 | 33,579,000,000 | 33,579.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 5 | 32,973,000,000 | 32,973.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 6 | 32,839,000,000 | 32,839.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 7 | 30,704,100,000 | 30,704.10 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 8 | 30,083,200,000 | 30,083.20 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 9 | 29,494,700,000 | 29,494.70 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 10 | 29,176,600,000 | 29,176.60 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 11 | 28,239,200,000 | 28,239.20 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 12 | 27,950,400,000 | 27,950.40 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 13 | 20,923,900,000 | 20,923.90 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2025'... |
| 14 | 20,529,700,000 | 20,529.70 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2025'... |
| 15 | 20,361,200,000 | 20,361.20 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2024'... |
| 16 | 20,283,700,000 | 20,283.70 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2024'... |
| 17 | 18,750,900,000 | 18,750.90 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2023'... |
| 18 | 18,427,100,000 | 18,427.10 | 1,000,000x | 16 | TABLE | Table 2, column 'FY 2023'... |
| 19 | 15,873,500,000 | 15,873.50 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2025'... |
| 20 | 15,815,600,000 | 15,815.60 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2025'... |
| 21 | 15,647,900,000 | 15,647.90 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2024'... |
| 22 | 15,464,700,000 | 15,464.70 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2024'... |
| 23 | 15,461,700,000 | 15,461.70 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2024'... |
| 24 | 15,250,400,000 | 15,250.40 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2025'... |
| 25 | 15,224,200,000 | 15,224.20 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2025'... |
| 26 | 15,197,600,000 | 15,197.60 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2024'... |
| 27 | 14,393,500,000 | 14,393.50 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2023'... |
| 28 | 13,996,100,000 | 13,996.10 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2023'... |
| 29 | 13,893,800,000 | 13,893.80 | 1,000,000x | 26 | TABLE | Table 4, column 'FY 2023'... |
| 30 | 13,821,200,000 | 13,821.20 | 1,000,000x | 26 | TABLE | Table 5, column 'FY 2023'... |
| 31 | 13,037,000,000 | 13,037.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 32 | 12,885,000,000 | 12,885.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 33 | 12,846,000,000 | 12,846.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2025'... |
| 34 | 12,705,000,000 | 12,705.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2024'... |
| 35 | 12,472,000,000 | 12,472.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 36 | 12,388,000,000 | 12,388.00 | 1,000,000x | 13 | TABLE | Table 1, column 'FY 2023'... |
| 37 | 9,982,000,000 | 9,982.00 | 1,000,000x | 17 | TABLE | Table 3, column 'FY 2023'... |
| 38 | 9,982,000,000 | 9,982.00 | 1,000,000x | 73 | TABLE | Table 53, column 'FY 2023'... |
| 39 | 9,821,000,000 | 9,821.00 | 1,000,000x | 72 | TABLE | Table 52, column 'FY 2023'... |
| 40 | 9,650,000,000 | 9,650.00 | 1,000,000x | 72 | TABLE | Table 52, column 'FY 2025'... |
| 41 | 9,637,000,000 | 9,637.00 | 1,000,000x | 17 | TABLE | Table 3, column 'FY 2023'... |
| 42 | 9,637,000,000 | 9,637.00 | 1,000,000x | 73 | TABLE | Table 53, column 'FY 2023'... |
| 43 | 9,600,000,000 | 9.60 | 1,000,000,000x | 1 | text | r, land, and sea transportation for the DoD with a primary focus on wartime read... |
| 44 | 9,600,000,000 | 9.60 | 1,000,000,000x | 1 | text | viding air, land, and sea transportation for the DoD with a primary focus on war... |
| 45 | 9,567,000,000 | 9,567.00 | 1,000,000x | 71 | TABLE | Table 51, column 'FY 2023'... |
| 46 | 9,554,000,000 | 9,554.00 | 1,000,000x | 71 | TABLE | Table 51, column 'FY 2025'... |
| 47 | 9,534,000,000 | 9,534.00 | 1,000,000x | 17 | TABLE | Table 3, column 'FY 2025'... |
| 48 | 9,534,000,000 | 9,534.00 | 1,000,000x | 73 | TABLE | Table 53, column 'FY 2025'... |
| 49 | 9,521,000,000 | 9,521.00 | 1,000,000x | 17 | TABLE | Table 3, column 'FY 2025'... |
| 50 | 9,521,000,000 | 9,521.00 | 1,000,000x | 73 | TABLE | Table 53, column 'FY 2025'... |
Results saved to results/
```

## Usage

### Basic Usage

```bash
# Analyze a PDF (uses Docling chunked retrieval by default)
python pdf_number_extractor.py path/to/document.pdf

# Use direct extraction (no chunking)
python pdf_number_extractor.py path/to/document.pdf --no-chunking

# Show top 50 candidates instead of default 20
python pdf_number_extractor.py path/to/document.pdf --top-n 50

# Specify custom output directory
python pdf_number_extractor.py path/to/document.pdf --output-dir my_results
```

### Why unit detection is non-trivial

Documents frequently contain ambiguous tokens like "11B" or "Chapter 14B" that
look like scale suffixes but are not numeric multipliers. This system explicitly
distinguishes inline numeric suffixes from contextual unit annotations to avoid
false inflation of values.
