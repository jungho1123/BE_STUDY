import os

base_dirs = [
    "app/api/dog_posts",
    "app/api/nose",
    "app/api/eye",
    "app/api/comic",
    "app/api/auth",
    "app/core",
    "app/models",
    "app/database/migrations",
    "app/schemas",
    "app/static/uploads",
]

# 각 폴더에 생성할 기본 파일 (해당 디렉토리에만 생성)
init_files = {
    "app/api/dog_posts": ["router.py", "service.py", "schema.py", "__init__.py"],
    "app/api/nose": ["router.py", "schema.py", "__init__.py"],
    "app/api/eye": ["router.py", "schema.py", "__init__.py"],
    "app/api/comic": ["router.py", "schema.py", "__init__.py"],
    "app/api/auth": ["router.py", "schema.py", "utils.py", "__init__.py"],
    "app/api": ["main_router.py"],
    "app/core": ["config.py", "security.py", "exceptions.py","constants.py"],
    "app/models": ["post.py", "user.py", "nose.py", "__init__.py"],
    "app/database": ["session.py", "base.py"],
    "app/schemas": ["common.py"],
    "app": ["main.py"],
}

# 디렉토리 생성
for path in base_dirs:
    os.makedirs(path, exist_ok=True)

# 파일 생성
for dir_path, files in init_files.items():
    for file in files:
        full_path = os.path.join(dir_path, file)
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")  # 비어 있는 파일 생성
