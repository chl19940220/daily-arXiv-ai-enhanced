today=$(date -u "+%Y-%m-%d")
year_month=$(date -u "+%Y-%m")
data_dir="data/${year_month}"
mkdir -p "${data_dir}"

cd daily_arxiv
scrapy crawl arxiv -o "../${data_dir}/${today}.jsonl"

cd ../ai
python enhance.py --data "../${data_dir}/${today}.jsonl"

cd ../to_md
language_code_for_file=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')
python convert.py --data "../${data_dir}/${today}_AI_enhanced_${language_code_for_file}.jsonl"

cd ..
python update_readme.py --data_dir "${data_dir}"
