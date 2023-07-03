import os
import sys
import subprocess
import openai

# OpenAI APIキーの設定
openai.api_key = "YOUR_API_KEY"

# Gitの差分を取得
diff_output = subprocess.check_output(["git", "diff"]).decode("utf-8")

# GPT-3.5に渡してコミットメッセージを生成
prompt = f"```Please make git commit messages for the following diff output.Each commit message must be one line starting with one of the following words.* feat: (new feature for the user, not a new feature for build script)* fix: (bug fix for the user, not a fix to a build script)* docs: (changes to the documentation)* style: (formatting, missing semi colons, etc; no production code change)* refactor: (refactoring production code, eg. renaming a variable)* test: (adding missing tests, refactoring tests; no production code change)* chore: (updating grunt tasks etc; no production code change)\n{diff_output}\n```"
response = openai.Completion.create(
  engine="text-davinci-003",
  prompt=prompt,
  temperature=0.5,
  max_tokens=100,
  n=1,
  stop=None,
)
commit_message = response.choices[0].text.strip()

# ユーザーに修正を求める
print("Generated commit message:")
print(commit_message)
print("\nPlease review and modify the commit message as needed.")
user_input = input("Press enter to continue or 'q' to quit without committing: ")

# コミットメッセージの修正を確認
if user_input.lower().strip() == "q":
  sys.exit(0)

# コミットを作成
subprocess.run(["git", "commit", "-am", commit_message])

print("Commit created successfully!")
