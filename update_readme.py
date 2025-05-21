import os
from os.path import join
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update README.md with links to daily arXiv summaries.")
    parser.add_argument("--data_dir", type=str, help="The specific YYYY-MM directory for the current run (not directly used for listing all files, but good for consistency).", default="data")
    args = parser.parse_args()

    template = open('template.md', 'r').read()
    readme_content_template = open('readme_content_template.md', 'r').read()
    
    all_monthly_links = []
    
    base_data_dir = "data"
    if not os.path.exists(base_data_dir):
        print(f"Warning: Base data directory '{base_data_dir}' does not exist.")
        monthly_subdirs = []
    else:
        monthly_subdirs = sorted(
            [d for d in os.listdir(base_data_dir) if os.path.isdir(join(base_data_dir, d)) and len(d) == 7 and d[4] == '-'],
            reverse=True
        )

    for month_dir in monthly_subdirs:
        month_path = join(base_data_dir, month_dir)
        daily_md_files = sorted(
            [f for f in os.listdir(month_path) if f.endswith('.md')],
            reverse=True
        )
        
        if not daily_md_files:
            continue

        month_section = f"### {month_dir}\n"
        daily_links = []
        for md_file in daily_md_files:
            date_str = md_file.replace('.md', '')
            file_url = join(month_path, md_file) 
            daily_links.append(readme_content_template.format(date=date_str, url=file_url))
        
        month_section += "\n".join(daily_links)
        all_monthly_links.append(month_section)

    readme_content = "\n\n".join(all_monthly_links)
    markdown = template.format(readme_content=readme_content)
    
    with open('README.md', 'w') as f:
        f.write(markdown)
