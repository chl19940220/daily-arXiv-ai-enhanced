today=$(date -u "+%Y-%m-%d")
year_month=$(date -u "+%Y-%m")
data_dir="data/${year_month}"
mkdir -p "${data_dir}"

temp_jsonl_file="${data_dir}/${today}.jsonl"

cd daily_arxiv
scrapy crawl arxiv -o "../${temp_jsonl_file}"

cd ../ai
echo "Current directory: $(pwd)"
echo "Running enhance.py with input: ../${temp_jsonl_file}"
python enhance.py --data "../${temp_jsonl_file}"
echo "enhance.py finished."

cd ..
rm "${temp_jsonl_file}"
echo "Cleaned up temporary JSONL file."