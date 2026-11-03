import re, sys, urllib.request, urllib.parse, http.cookiejar
q = sys.argv[1]
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"),
                 ("Accept-Language", "zh-CN,zh;q=0.9")]
url = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else "https://www.sogou.com/web?query=" + urllib.parse.quote(q)
s = op.open(url, timeout=20).read().decode("utf-8", "ignore")
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
t = re.sub(r"<[^>]+>", " ", t)
t = re.sub(r"\s+", " ", t)
for kw in sys.argv[3:] or [q.split()[0]]:
    for m in re.finditer(re.escape(kw), t):
        print("...", t[max(0, m.start() - 250): m.end() + 250], "\n")
print("LEN", len(s), "links:", sorted(set(re.findall(r'href="(https?://[^"]+)"', s)))[:40])
