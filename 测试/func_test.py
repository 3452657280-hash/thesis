"""系统功能黑盒测试：通过后端 HTTP 接口逐项执行用例，记录预期与实际结果。
在演示(mock)模式实例上运行，不消耗 Coze 积分；智能体真实回答质量由 run_eval.py 单独测试。
用法：python func_test.py [--base http://localhost:8082]
"""
import argparse
import csv
import datetime
import json
import os
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


class Api:
    def __init__(self, base):
        self.base = base

    def req(self, method, path, token=None, body=None, raw=False):
        r = urllib.request.Request(self.base + path, method=method)
        r.add_header("Content-Type", "application/json")
        if token:
            r.add_header("Authorization", "Bearer " + token)
        data = json.dumps(body).encode() if body is not None else None
        try:
            with urllib.request.urlopen(r, data=data, timeout=60) as resp:
                text = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8")
            status = e.code
        if raw:
            return status, text
        try:
            return status, json.loads(text)
        except ValueError:
            return status, {"raw": text[:200]}

    def login(self, u, p):
        s, j = self.req("POST", "/api/auth/login", body={"username": u, "password": p})
        return j.get("data", {}).get("token") if s == 200 and j.get("code") == 200 else None

    def chat(self, token, sid, content):
        r = urllib.request.Request(f"{self.base}/api/consult/sessions/{sid}/chat", method="POST")
        r.add_header("Content-Type", "application/json")
        r.add_header("Authorization", "Bearer " + token)
        events, ev = [], None
        with urllib.request.urlopen(r, data=json.dumps({"content": content}).encode(), timeout=120) as resp:
            for line in resp:
                line = line.decode("utf-8").rstrip("\r\n")
                if line.startswith("event:"):
                    ev = line[6:].strip()
                elif line.startswith("data:"):
                    events.append((ev, json.loads(line[5:].strip())))
        return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8082")
    a = ap.parse_args()
    api = Api(a.base)
    results = []

    def case(cid, module, item, steps, expected, fn):
        try:
            ok, actual = fn()
        except Exception as e:
            ok, actual = False, f"异常：{e}"
        results.append({"编号": cid, "模块": module, "测试项": item, "操作步骤": steps,
                        "预期结果": expected, "实际结果": actual, "结论": "通过" if ok else "不通过"})
        print(cid, "通过" if ok else "不通过", actual)

    stamp = datetime.datetime.now().strftime("%H%M%S")
    uname = f"ft_{stamp}"
    ctx = {}

    def t_reg():
        s, j = api.req("POST", "/api/auth/register", body={"username": uname, "password": "abc123", "nickname": "测试用户", "role": "USER"})
        return j.get("code") == 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F01", "用户认证", "用户注册", "填写合法用户名、密码提交注册", "注册成功", t_reg)

    def t_reg_dup():
        s, j = api.req("POST", "/api/auth/register", body={"username": uname, "password": "abc123", "role": "USER"})
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F02", "用户认证", "重复用户名注册", "使用已存在的用户名再次注册", "提示用户名已存在，注册失败", t_reg_dup)

    def t_reg_bad():
        s, j = api.req("POST", "/api/auth/register", body={"username": "ab", "password": "1", "role": "USER"})
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F03", "用户认证", "非法参数注册", "用户名2位、密码1位提交注册", "参数校验失败并给出提示", t_reg_bad)

    def t_login():
        ctx["u"] = api.login(uname, "abc123")
        return ctx["u"] is not None, "返回JWT令牌" if ctx["u"] else "未返回令牌"
    case("F04", "用户认证", "正确密码登录", "输入正确用户名和密码登录", "登录成功并返回令牌", t_login)

    def t_login_bad():
        s, j = api.req("POST", "/api/auth/login", body={"username": uname, "password": "wrong1"})
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F05", "用户认证", "错误密码登录", "输入错误密码登录", "登录失败并提示", t_login_bad)

    def t_noauth():
        s, j = api.req("GET", "/api/consult/sessions")
        return s == 401, f"HTTP {s} msg={j.get('msg')}"
    case("F06", "权限控制", "未登录访问受保护接口", "不携带令牌请求会话列表", "返回401未登录", t_noauth)

    def t_forbid():
        s, j = api.req("GET", "/api/admin/users", ctx["u"])
        return s == 403, f"HTTP {s} msg={j.get('msg')}"
    case("F07", "权限控制", "普通用户访问管理接口", "以USER身份请求管理员用户列表", "返回403权限不足", t_forbid)

    def t_new_session():
        s, j = api.req("POST", "/api/consult/sessions", ctx["u"], body={})
        ctx["sid"] = j.get("data", {}).get("id")
        return ctx["sid"] is not None, f"会话id={ctx['sid']} 标题={j.get('data', {}).get('title')}"
    case("F08", "智能咨询", "新建会话", "点击“新建咨询”", "生成新会话", t_new_session)

    def t_chat():
        ev = api.chat(ctx["u"], ctx["sid"], "公司拖欠工资怎么办？")
        names = [e for e, _ in ev]
        done = [d for e, d in ev if e == "done"]
        ok = names.count("delta") > 1 and len(done) == 1 and done[0].get("messageId")
        ctx["mid"] = done[0].get("messageId") if done else None
        return bool(ok), f"收到delta事件{names.count('delta')}个，done事件{len(done)}个"
    case("F09", "智能咨询", "流式问答", "在会话中发送问题", "回答以多段增量逐步推送，结束时返回done事件", t_chat)

    def t_history():
        s, j = api.req("GET", f"/api/consult/sessions/{ctx['sid']}/messages", ctx["u"])
        msgs = j.get("data") or []
        roles = [m.get("role") for m in msgs]
        return roles == ["user", "assistant"], f"消息角色序列={roles}"
    case("F10", "智能咨询", "历史消息保存", "重新打开该会话查看消息", "依次显示用户问题和智能体回答", t_history)

    def t_title():
        s, j = api.req("GET", "/api/consult/sessions", ctx["u"])
        t = next((x.get("title") for x in j.get("data") or [] if x.get("id") == ctx["sid"]), None)
        return t == "公司拖欠工资怎么办？", f"会话标题={t}"
    case("F11", "智能咨询", "会话标题自动生成", "首次提问后查看会话列表", "标题为问题前20字", t_title)

    def t_fav():
        s, j = api.req("POST", f"/api/consult/messages/{ctx['mid']}/favorite", ctx["u"])
        s2, j2 = api.req("GET", "/api/consult/favorites", ctx["u"])
        n = len(j2.get("data") or [])
        return j.get("code") == 200 and n == 1, f"收藏后收藏列表条数={n}"
    case("F12", "智能咨询", "收藏回答", "点击回答下方“收藏”", "收藏成功并出现在我的收藏", t_fav)

    def t_fb():
        s, j = api.req("POST", f"/api/consult/messages/{ctx['mid']}/feedback", ctx["u"], body={"score": 5, "comment": "清楚"})
        return j.get("code") == 200, f"code={j.get('code')}"
    case("F13", "智能咨询", "评价回答", "对回答打5分并填写评语", "评价提交成功", t_fb)

    def t_other_session():
        t2 = api.login("user1", "123456")
        s, j = api.req("GET", f"/api/consult/sessions/{ctx['sid']}/messages", t2)
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F14", "智能咨询", "越权访问他人会话", "用户user1请求其他用户的会话消息", "提示会话不存在，拒绝访问", t_other_session)

    def t_laws():
        s, j = api.req("GET", "/api/public/laws?keyword=%E6%8B%96%E6%AC%A0&page=1&size=5")
        d = j.get("data") or {}
        return j.get("code") == 200 and d.get("total", 0) > 0, f"关键词“拖欠”命中{d.get('total')}条"
    case("F15", "法条查询", "关键词检索法条", "输入关键词“拖欠”检索", "返回包含该关键词的法条分页结果", t_laws)

    def t_law_names():
        s, j = api.req("GET", "/api/public/laws/names")
        n = len(j.get("data") or [])
        return n == 6, f"法律名称数={n}"
    case("F16", "法条查询", "按法律筛选", "打开法律名称下拉框", "列出6部法律", t_law_names)

    def t_lawyers():
        s, j = api.req("GET", "/api/public/lawyers?page=1&size=10")
        d = j.get("data") or {}
        ctx["lawyer_id"] = (d.get("records") or [{}])[0].get("id")
        return d.get("total", 0) >= 1, f"已审核律师数={d.get('total')}"
    case("F17", "律师预约", "浏览律师列表", "打开律师列表页面", "仅显示审核通过的律师", t_lawyers)

    def t_appt():
        when = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        s, j = api.req("POST", "/api/appointments", ctx["u"], body={"lawyerId": ctx["lawyer_id"], "question": "劳动合同到期不续签有补偿吗？", "appointTime": when})
        return j.get("code") == 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F18", "律师预约", "提交预约", "选择律师，填写问题和期望时间提交", "预约成功，状态为待处理", t_appt)

    def t_appt_past():
        s, j = api.req("POST", "/api/appointments", ctx["u"], body={"lawyerId": ctx["lawyer_id"], "question": "测试", "appointTime": "2020-01-01 10:00:00"})
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F19", "律师预约", "预约时间早于当前", "期望时间填写过去的日期", "提示时间不合法，预约失败", t_appt_past)

    def t_lawyer_handle():
        ctx["l"] = api.login("lawyer1", "123456")
        s, j = api.req("GET", "/api/lawyer/appointments", ctx["l"])
        recs = j.get("data") or []
        aid = next((x["id"] for x in recs if x.get("question") == "劳动合同到期不续签有补偿吗？"), None)
        s2, j2 = api.req("PUT", f"/api/lawyer/appointments/{aid}", ctx["l"], body={"status": 1, "reply": "已接受，明天电话联系"})
        s3, j3 = api.req("GET", "/api/appointments/my", ctx["u"])
        st = next((x.get("status") for x in j3.get("data") or [] if x.get("id") == aid), None)
        ctx["aid"] = aid
        return j2.get("code") == 200 and st == 1, f"律师接受后用户端看到状态={st}"
    case("F20", "律师端", "处理预约", "律师登录后接受预约并回复", "预约状态变为已接受，用户端同步可见", t_lawyer_handle)

    def t_lawyer_bad_state():
        s, j = api.req("PUT", f"/api/lawyer/appointments/{ctx['aid']}", ctx["l"], body={"status": 2, "reply": "拒绝"})
        return j.get("code") != 200, f"code={j.get('code')} msg={j.get('msg')}"
    case("F21", "律师端", "非法状态流转", "对已接受的预约执行“拒绝”", "提示当前状态不允许该操作", t_lawyer_bad_state)

    def t_cert():
        lname = f"fl_{stamp}"
        api.req("POST", "/api/auth/register", body={"username": lname, "password": "abc123", "role": "LAWYER"})
        tl = api.login(lname, "abc123")
        s, j = api.req("POST", "/api/lawyer/profile", tl, body={"realName": "李测试", "licenseNo": "TEST-0001", "lawFirm": "测试律所", "specialty": "消费维权", "years": 3, "intro": "功能测试数据"})
        ctx["new_lawyer"] = lname
        s2, j2 = api.req("GET", "/api/lawyer/profile", tl)
        st = (j2.get("data") or {}).get("auditStatus")
        return j.get("code") == 200 and st == 0, f"提交后审核状态={st}"
    case("F22", "律师端", "提交资质认证", "律师填写执业信息提交", "提交成功，状态为待审核", t_cert)

    def t_admin_audit():
        ctx["a"] = api.login("admin", "admin123")
        s, j = api.req("GET", "/api/admin/lawyers?auditStatus=0", ctx["a"])
        recs = j.get("data") or []
        pid = next((x["id"] for x in recs if x.get("realName") == "李测试"), None)
        s2, j2 = api.req("PUT", f"/api/admin/lawyers/{pid}/audit", ctx["a"], body={"auditStatus": 1, "auditRemark": "资料齐全"})
        s3, j3 = api.req("GET", "/api/public/lawyers?page=1&size=50")
        names = [x.get("realName") for x in (j3.get("data") or {}).get("records") or []]
        return j2.get("code") == 200 and "李测试" in names, f"审核通过后公开律师列表包含该律师={'李测试' in names}"
    case("F23", "管理员端", "律师资质审核", "管理员审核通过待审律师", "该律师出现在公开律师列表", t_admin_audit)

    def t_admin_disable():
        s, j = api.req("GET", f"/api/admin/users?keyword={uname}&page=1&size=10", ctx["a"])
        uid = ((j.get("data") or {}).get("records") or [{}])[0].get("id")
        api.req("PUT", f"/api/admin/users/{uid}/status", ctx["a"], body={"status": 0})
        tok = api.login(uname, "abc123")
        api.req("PUT", f"/api/admin/users/{uid}/status", ctx["a"], body={"status": 1})
        return tok is None, "禁用后登录被拒绝" if tok is None else "禁用后仍可登录"
    case("F24", "管理员端", "禁用用户", "管理员禁用某用户后该用户登录", "被禁用用户无法登录", t_admin_disable)

    def t_admin_law():
        body = {"lawName": "测试法", "chapter": "第一章", "articleNo": "第一条", "content": "功能测试条文"}
        s, j = api.req("POST", "/api/admin/laws", ctx["a"], body=body)
        s2, j2 = api.req("GET", "/api/admin/laws?keyword=%E5%8A%9F%E8%83%BD%E6%B5%8B%E8%AF%95%E6%9D%A1%E6%96%87&page=1&size=5", ctx["a"])
        recs = (j2.get("data") or {}).get("records") or []
        lid = recs[0]["id"] if recs else None
        s3, j3 = api.req("DELETE", f"/api/admin/laws/{lid}", ctx["a"])
        return j.get("code") == 200 and lid and j3.get("code") == 200, f"新增后检索到{len(recs)}条，删除code={j3.get('code')}"
    case("F25", "管理员端", "法条维护", "管理员新增一条法条再删除", "新增、查询、删除均成功", t_admin_law)

    def t_admin_stats():
        s, j = api.req("GET", "/api/admin/stats", ctx["a"])
        d = j.get("data") or {}
        keys = ["userCount", "lawyerCount", "sessionCount", "questionCount", "dailyQuestions", "scoreDistribution"]
        return all(k in d for k in keys) and len(d.get("dailyQuestions") or []) == 14, f"问题数={d.get('questionCount')} 近14天数据点={len(d.get('dailyQuestions') or [])}"
    case("F26", "管理员端", "数据统计", "打开管理员首页统计看板", "返回用户数、咨询量、近14天趋势和评分分布", t_admin_stats)

    def t_admin_records():
        s, j = api.req("GET", "/api/admin/consults?page=1&size=10", ctx["a"])
        d = j.get("data") or {}
        return d.get("total", 0) >= 1, f"问答记录总数={d.get('total')}"
    case("F27", "管理员端", "查看问答记录", "打开咨询记录页面", "列出全部用户的问答记录", t_admin_records)

    def t_del_session():
        s, j = api.req("DELETE", f"/api/consult/sessions/{ctx['sid']}", ctx["u"])
        s2, j2 = api.req("GET", "/api/consult/sessions", ctx["u"])
        left = [x for x in j2.get("data") or [] if x.get("id") == ctx["sid"]]
        return j.get("code") == 200 and not left, f"删除后会话残留={len(left)}"
    case("F28", "智能咨询", "删除会话", "删除一个已有会话", "会话及其消息被删除", t_del_session)

    out = os.path.join(HERE, f"功能测试结果_{datetime.date.today():%Y%m%d}.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"共{len(results)}项，通过{sum(r['结论'] == '通过' for r in results)}项。结果：{out}")


if __name__ == "__main__":
    main()
