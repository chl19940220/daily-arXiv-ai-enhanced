today=$(date -u "+%Y-%m-%d")
year_month=$(date -u "+%Y-%m")
data_dir="data/${year_month}"
mkdir -p "${data_dir}"
language_code_for_file=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')

cd daily_arxiv
scrapy crawl arxiv -o "../${data_dir}/${today}.jsonl"

cd ../ai
echo "Current directory: $(pwd)"
echo "Running enhance.py with input: ../${data_dir}/${today}.jsonl"
python enhance.py --data "../${data_dir}/${today}.jsonl"
echo "enhance.py finished."

# --- BEGIN DEBUG ---
echo "Listing contents of ${data_dir} before running convert.py:"
ls -l "../${data_dir}/" 
echo "Expected file for convert.py: ../${data_dir}/${today}_AI_enhanced_${language_code_for_file}.jsonl"
# --- END DEBUG ---

cd ../to_md
language_code_for_file=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')
echo "Running convert.py with input: ../${data_dir}/${today}_AI_enhanced_${language_code_for_file}.jsonl"
python convert.py --data "../${data_dir}/${today}_AI_enhanced_${language_code_for_file}.jsonl"

cd ..
python update_readme.py --data_dir "${data_dir}"
