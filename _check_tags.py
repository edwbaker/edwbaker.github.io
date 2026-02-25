import os, yaml, glob

posts_dir = r'c:\Users\edwab\OneDrive - Natural History Museum\Documents\GitHub\edwbaker.github.io\_posts'
for f in glob.glob(os.path.join(posts_dir, '**', '*.md'), recursive=True):
    with open(f, encoding='utf-8') as fh:
        content = fh.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                if fm and 'tags' in fm:
                    tags = fm['tags']
                    print(f"{os.path.basename(f)}: tags={tags} (type={type(tags).__name__})")
            except Exception as e:
                print(f"YAML ERROR in {os.path.basename(f)}: {e}")
