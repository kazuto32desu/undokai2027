#!/usr/bin/env python3
"""ポスターQRの転送先を切り替える。

    python3 set_dest.py "https://docs.google.com/forms/d/e/xxxx/viewform"   # 転送先を設定
    python3 set_dest.py --clear                                            # 「準備中」表示に戻す

index.html を作り直して commit & push する。GitHub Pages は反映時にCDNを更新するので、
1〜2分で切り替わる。QRコードの行き先（このサイトのURL）は変わらない。
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
TITLE = "動物病院大運動会2027 お申し込み"

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
{refresh}<style>
  body {{
    margin: 0; padding: 15vh 24px 24px;
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    text-align: center; color: #1a1a1a; background: #fff; line-height: 1.9;
  }}
  .accent {{ color: #e8503a; font-weight: 700; letter-spacing: .08em; font-size: 13px; }}
  h1 {{ font-size: 17px; font-weight: 600; margin: 12px 0 24px; }}
  a {{ color: #e8503a; }}
  .note {{ color: #777; font-size: 13px; margin-top: 32px; }}
</style>
</head>
<body>
<p class="accent">動物病院大運動会 2027</p>
"""

FOOT = """</body>
</html>
"""

REDIRECT_BODY = """<h1>お申し込みページへ移動します…</h1>
<p><a href="{url}">移動しない場合はこちらをタップ</a></p>
<script>location.replace({json_url});</script>
"""

PENDING_BODY = """<h1>お申し込みページは準備中です</h1>
<p class="note">受付開始までしばらくお待ちください。<br>このページはそのままご利用いただけます。</p>
"""


def build(url: str | None) -> str:
    if url:
        esc = url.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        head = HEAD.format(
            title=TITLE,
            refresh=f'<meta http-equiv="refresh" content="0;url={esc}">\n',
        )
        # JSON文字列として埋め込み、引用符やバックスラッシュを安全に扱う
        body = REDIRECT_BODY.format(url=esc, json_url=f'"{url}"')
    else:
        head = HEAD.format(title=TITLE, refresh="")
        body = PENDING_BODY
    return head + body + FOOT


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    arg = sys.argv[1].strip()

    if arg == "--clear":
        url = None
        message = "転送先をクリア（準備中表示）"
    else:
        if not re.match(r"^https://[^\s\"'<>]+$", arg):
            print(f"エラー: https:// で始まる正しいURLを指定してください（受け取った値: {arg!r}）")
            return 1
        url = arg
        message = f"転送先を設定: {url}"

    (HERE / "index.html").write_text(build(url), encoding="utf-8")

    subprocess.run(["git", "add", "index.html"], cwd=HERE, check=True)
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=HERE, capture_output=True, text=True
    )
    if result.returncode != 0 and "nothing to commit" not in result.stdout:
        print(result.stdout, result.stderr)
        return 1
    subprocess.run(["git", "push", "origin", "main"], cwd=HERE, check=True)

    print(message)
    print("GitHub Pages への反映まで1〜2分かかります。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
