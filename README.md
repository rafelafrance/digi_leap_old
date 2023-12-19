# traiter_llm![CI](https://github.com/rafelafrance/traiter_llm/workflows/CI/badge.svg)
Get traits from a large language model

## General workflow
1. Have a set of OCRed labels or treatments in a directory, one text file per label or treatment.
2. **get_gpt_output.py**: Send each file from step 1 to the OpenAI server for parsing.
3. **clean_gpt_output.py**: Clean the ChatGPT output from step 2.
