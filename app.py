# CMS v2 - Single File - Drag Anywhere + Hamburger + Trash Next To LIVE
# Run: cd Desktop -> python cms-v2.py -> http://localhost:5000/admin
import os, json, uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data.json")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cms-change-this-secret")
UPLOAD_DIR = os.path.join(BASE, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
ALLOWED_VIDEO = {".mp4",".webm",".mov",".m4v"}
def load():
    if not os.path.exists(DATA_FILE):
        d = {"pages":[
            {"id":"home","title":"Home","slug":"home","status":"live","menu":True,"menu_label":"Home","updated":"2026-11-19","blocks":[
                {"id":"b1","type":"heading","content":"Welcome to My Shop","x":40,"y":40,"w":600,"style":{"color":"#111827","fontSize":42}},
                {"id":"b2","type":"text","content":"Tap + Add Block, then drag it anywhere. Tap Publish to go live!","x":40,"y":130,"w":560,"style":{"color":"#4b5563","fontSize":18}},
                {"id":"b3","type":"button","content":"Shop Now","x":40,"y":210,"w":180,"style":{"color":"#ffffff","background":"#111827","fontSize":16}},
                {"id":"b4","type":"image","content":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900","x":40,"y":280,"w":500,"style":{}}
            ]},
            {"id":"shop","title":"Shop","slug":"shop","status":"live","menu":True,"menu_label":"Shop","updated":"2026-11-19","blocks":[
                {"id":"b1","type":"heading","content":"Shop All","x":40,"y":40,"w":500,"style":{"color":"#111827","fontSize":36}},
                {"id":"b2","type":"product","content":"Brass Gear Buckle - $85","x":40,"y":120,"w":320,"style":{}}
            ]},
            {"id":"about","title":"About","slug":"about","status":"draft","menu":False,"menu_label":"About","updated":"2026-11-19","blocks":[
                {"id":"b1","type":"heading","content":"About Us","x":40,"y":40,"w":500,"style":{"color":"#111827","fontSize":36}},
                {"id":"b2","type":"text","content":"We make handmade buckles.","x":40,"y":120,"w":500,"style":{"color":"#333","fontSize":18}}
            ]}
        ],
        "products":[{"id":"p1","name":"Brass Gear Buckle","price":85,"image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600","stock":12}],
        "site":{"name":"My Shop","logo":"\U0001f3ea","menu_color":"#111827","show_hamburger":True}}
        json.dump(d, open(DATA_FILE,"w"), indent=2)
        return d
    d = json.load(open(DATA_FILE))
    if "site" not in d:
        d["site"] = {"name":"My Shop","logo":"\U0001f3ea","menu_color":"#111827","show_hamburger":True}
    if "admin" not in d:
        d["admin"] = None
    if "products" not in d:
        d["products"] = []
    if "pages" not in d:
        d["pages"] = []
    for pg in d["pages"]:
        pg.setdefault("menu", True)
        pg.setdefault("menu_label", pg.get("title","Untitled"))
        pg.setdefault("status", "draft")
        for b in pg.get("blocks", []):
            b.setdefault("x", 40); b.setdefault("y", 40); b.setdefault("w", 320); b.setdefault("style", {})
    try: json.dump(d, open(DATA_FILE,"w"), indent=2)
    except: pass
    return d
def save(d): json.dump(d, open(DATA_FILE,"w"), indent=2)

ADMIN = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard - CMS v2</title><style>body{font-family:sans-serif;max-width:900px;margin:20px auto;padding:16px} .card{border:1px solid #e5e7eb;padding:16px;border-radius:16px;margin:12px 0;display:flex;justify-content:space-between;align-items:center} .btn{background:#111827;color:#fff;border:0;padding:10px 16px;border-radius:10px;cursor:pointer;text-decoration:none} .live{background:#dcfce7;padding:6px 12px;border-radius:20px;font-weight:700} .draft{background:#fef9c3;padding:6px 12px;border-radius:20px;font-weight:700} .trash{background:#fee2e2;border:2px solid #dc2626;color:#dc2626;font-size:22px;padding:6px 11px;border-radius:10px;cursor:pointer;line-height:1} .trash:hover{background:#dc2626;color:#fff} input{padding:12px;border-radius:10px;border:1px solid #ddd;width:280px} @media(max-width:600px){.card{flex-direction:column;align-items:flex-start;gap:10px}}</style></head><body>
<div style="display:flex;justify-content:space-between"><h1>\U0001f44b {{site.name}} - v3</h1><a href="/logout" style="background:#fee2e2;color:#111;padding:10px 14px;border-radius:10px;text-decoration:none;font-weight:700">Log Out</a></div><p>Step 1: Make a page &nbsp;•&nbsp; Step 2: Drag stuff anywhere &nbsp;•&nbsp; Step 3: Hit Publish</p>
<input id="t" placeholder="What should your new page be called?"><button class="btn" onclick="createPage()">+ New Page</button>
<h2>Your Pages - Trash is RIGHT NEXT TO Live</h2>
{% for p in pages %}<div class="card"><div><b style="font-size:18px">{{p.title}}</b><br><small>/live/{{p.slug}} &bull; {% if p.menu %}\u2630 In Menu{% else %}Hidden from menu{% endif %}</small></div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="{{p.status}}">{{p.status}}</span> <button class="trash" title="Delete this page - even if it is LIVE" onclick="deletePage('{{p.id}}','{{p.title}}')">\U0001f5d1\ufe0f</button> <a class="btn" href="/builder/{{p.id}}">\u270f\ufe0f Edit</a> {% if p.status=='live' %}<a class="btn" href="/live/{{p.slug}}">\U0001f440 View Live</a>{% endif %} <button class="btn" style="background:#fee2e2;color:#111" onclick="toggleMenu('{{p.id}}',{{'false' if p.menu else 'true'}})">{% if p.menu %}Remove from Menu{% else %}Add to Menu{% endif %}</button></div></div>{% endfor %}
<script>async function createPage(){let t=document.getElementById('t').value||'Untitled';let r=await fetch('/api/pages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:t})});let j=await r.json();location.href='/builder/'+j.id} async function deletePage(id,title){if(!confirm('Delete \\''+title+'\\' FOREVER?\\nEven if it is LIVE, it will be gone and the live link will stop working.\\nThis cannot be undone.'))return;let r=await fetch('/api/pages/'+id,{method:'DELETE'});if(r.ok){alert('Deleted!');location.reload()}else{alert('Could not delete - try again')}} async function toggleMenu(id,v){await fetch('/api/pages/'+id+'/menu',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({menu:v})});location.reload()}</script></body></html>
"""
BUILDER = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Builder - {{page.title}}</title><style>*{box-sizing:border-box}body{margin:0;font-family:sans-serif;display:flex;height:100vh;overflow:hidden} .left{width:230px;background:#111827;color:#fff;padding:14px;overflow:auto;flex-shrink:0} .left button{width:100%;padding:12px;margin:6px 0;border-radius:10px;border:0;background:#fff;font-weight:700;cursor:pointer;font-size:15px} .canvas-wrap{flex:1;display:flex;flex-direction:column;background:#e5e7eb} .top{background:#fff;padding:10px 14px;display:flex;gap:8px;justify-content:space-between;align-items:center;border-bottom:1px solid #ddd;flex-wrap:wrap} .btn{background:#111827;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer} .btn.green{background:#16a34a} .trash2{background:#fee2e2;border:2px solid #dc2626;color:#dc2626;font-size:18px;padding:4px 9px;border-radius:10px;cursor:pointer;margin-left:6px} #canvas{position:relative;flex:1;margin:14px;background:#fff;border-radius:16px;overflow:auto;min-height:500px} .blk{position:absolute;border:2px dashed transparent;padding:10px;border-radius:10px;cursor:move;touch-action:none;user-select:none} .blk:hover{border-color:#cbd5e1} .blk.sel{border-color:#111827;background:#f8fafc} .right{width:270px;background:#fff;padding:14px;border-left:1px solid #e5e7eb;overflow:auto;flex-shrink:0} input,textarea{width:100%;padding:10px;margin:6px 0;border:1px solid #ddd;border-radius:10px} .tip{background:#fef9c3;padding:10px;border-radius:10px;font-size:13px}</style></head><body>
<div class="left"><h2>\U0001f9f1 Add Stuff</h2><div class="tip">\U0001f446 Tap a button to add it. Then DRAG it anywhere!</div><button onclick="add('heading')">\U0001f524 Heading</button><button onclick="add('text')">\U0001f4dd Text</button><button onclick="add('image')">\U0001f5bc\ufe0f Picture</button><button onclick="add('button')">\U0001f518 Button</button><button onclick="add('code')">\u003c/\u003e Raw Code - HTML / CSS / JS / Three.js</button><button onclick="add('video')">\u25b6\ufe0f Video</button><button onclick="add('divider')">\u2796 Line</button><hr><h3>\u25b6\ufe0f Upload Video</h3><p style="font-size:12px;opacity:.8">Pick a video file, or paste a YouTube / video link in the Video box.</p><input type="file" id="videoFile" accept="video/*" style="background:#fff;color:#111"><button onclick="uploadVideo()" style="background:#16a34a">\u2b06\ufe0f Upload Video File</button><p id="uploadMsg" style="font-size:12px"></p><hr><h3>\u2630 Menu</h3><label><input type="checkbox" id="inMenu" {{'checked' if page.menu else ''}} onchange="saveMenu()"> Show this page in hamburger menu</label><br><label>Menu Name</label><input id="menuLabel" value="{{page.menu_label or page.title}}" onchange="saveMenu()"><a href="/admin" style="color:#fff">\u2190 Back to Dashboard</a></div>
<div class="canvas-wrap"><div class="top"><b>{{page.title}} &mdash; <span id="st">{{page.status}}</span> <button class="trash2" onclick="deletePage()" title="Delete this page - even if LIVE">\U0001f5d1\ufe0f</button></b><div><button class="btn" onclick="preview()">\U0001f440 Preview</button><button class="btn" onclick="copyLink()">\U0001f4cb Copy Live Link</button><button class="btn" onclick="saveDraft()">\U0001f4be Save Draft</button><button class="btn green" onclick="publish()">\U0001f680 Publish = Live</button></div></div><div style="padding:8px 14px;font-size:13px;background:#fff;border-bottom:1px solid #eee">\U0001f4a1 <b>How to use:</b> Drag any box to move it &bull; Tap a box to edit it on the right</div><div id="canvas"></div></div>
<div class="right"><h3>\u270f\ufe0f Edit</h3><p id="nosel">Tap any box on the canvas to edit it here.</p><div id="ed" style="display:none"><label>What should it say?</label><textarea id="content" rows="4"></textarea><label>Text Color</label><input id="color" type="color"><label>Size</label><input id="fs" type="number"><label>Button / Background Color</label><input id="bg" type="color"><label>Width</label><input id="w" type="number"><button class="btn" onclick="apply()" style="width:100%">\u2705 Done</button><button class="btn" onclick="del()" style="width:100%;margin-top:8px;background:#dc2626">\U0001f5d1\ufe0f Delete This Box</button></div></div>
<script>
let page = {{page|tojson}}; let sel=null;
function render(){let c=document.getElementById('canvas');c.innerHTML='';page.blocks.forEach((b,i)=>{let d=document.createElement('div');d.className='blk'+(sel===i?' sel':'');d.style.left=b.x+'px';d.style.top=b.y+'px';d.style.width=(b.w||300)+'px';let inner='';if(b.type==='heading')inner=`<h2 style="margin:0;color:${b.style?.color||'#111'};font-size:${b.style?.fontSize||32}px">${b.content}</h2>`;else if(b.type==='text')inner=`<p style="margin:0;color:${b.style?.color||'#333'};font-size:${b.style?.fontSize||18}px">${b.content}</p>`;else if(b.type==='image')inner=`<img src="${b.content}" style="width:100%;border-radius:10px">`;else if(b.type==='button')inner=`<button style="background:${b.style?.background||'#111827'};color:#fff;padding:14px 22px;border-radius:10px;border:0;width:100%">${b.content}</button>`;else if(b.type==='product')inner=`<div style="border:1px solid #eee;padding:12px;border-radius:12px"><b>\U0001f6cd\ufe0f ${b.content}</b></div>`;else if(b.type==='video'){let v=b.content||''; if(v.includes('youtube.com')||v.includes('youtu.be')){let vid=v.split('v=')[1]?.split('&')[0]||v.split('/').pop(); inner=`<iframe width="100%" height="220" src="https://www.youtube.com/embed/${vid}" frameborder="0" allowfullscreen></iframe>`;} else if(v.startsWith('/')||v.endsWith('.mp4')||v.endsWith('.webm')||v.endsWith('.mov')){inner=`<video controls style="width:100%;border-radius:10px"><source src="${v}"></video>`;} else if(v.startsWith('http')){inner=`<video controls style="width:100%;border-radius:10px"><source src="${v}"></video>`;} else {inner=`<div style="background:#000;color:#fff;padding:36px;text-align:center;border-radius:10px">\u25b6 ${v}</div>`;}} else if(b.type==='code')inner=`<div style="background:#0f172a;color:#22c55e;padding:12px;border-radius:10px;font-size:12px"><b>Raw Code Block - runs live</b></div>`;else if(b.type==='divider')inner=`<hr>`;else inner=b.content;d.innerHTML=inner;d.addEventListener('pointerdown',e=>{sel=i;showEd();let sx=e.clientX-b.x, sy=e.clientY-b.y;let move=ev=>{b.x=Math.max(0,ev.clientX-sx);b.y=Math.max(0,ev.clientY-sy);render();};let up=()=>{document.removeEventListener('pointermove',move);document.removeEventListener('pointerup',up)};document.addEventListener('pointermove',move);document.addEventListener('pointerup',up);});c.appendChild(d);});document.getElementById('st').innerText=page.status;}
function add(t){let d={heading:'New Heading',text:'Write something here...',image:'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900',button:'Click Me',video:'My Video',divider:'---'};page.blocks.push({id:Date.now().toString(),type:t,content:d[t],x:60+page.blocks.length*20,y:60+page.blocks.length*20,w:320,style:{}});sel=page.blocks.length-1;render();showEd();}
function showEd(){if(sel===null)return;document.getElementById('nosel').style.display='none';document.getElementById('ed').style.display='block';let b=page.blocks[sel];document.getElementById('content').value=b.content;document.getElementById('color').value=b.style?.color||'#111827';document.getElementById('fs').value=parseInt(b.style?.fontSize||18);document.getElementById('bg').value=b.style?.background||'#111827';document.getElementById('w').value=b.w||320;}
function apply(){let b=page.blocks[sel];b.content=document.getElementById('content').value;b.style=b.style||{};b.style.color=document.getElementById('color').value;b.style.fontSize=document.getElementById('fs').value;b.style.background=document.getElementById('bg').value;b.w=parseInt(document.getElementById('w').value||320);render();}
function del(){page.blocks.splice(sel,1);sel=null;document.getElementById('ed').style.display='none';document.getElementById('nosel').style.display='block';render();}
async function uploadVideo(){let f=document.getElementById('videoFile').files[0]; if(!f){alert('Pick a video file first');return;} document.getElementById('uploadMsg').innerText='Uploading...'; let fd=new FormData(); fd.append('file', f); let r=await fetch('/api/upload',{method:'POST',body:fd}); let j=await r.json(); if(j.url){ document.getElementById('uploadMsg').innerText='Uploaded!'; page.blocks.push({id:Date.now().toString(),type:'video',content:j.url,x:60,y:60,w:480,style:{}}); sel=page.blocks.length-1; render(); showEd(); } else { document.getElementById('uploadMsg').innerText='Upload failed: '+(j.error||''); }} async function saveDraft(){page.status='draft';await fetch('/api/pages/'+page.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(page)});alert('Saved as Draft');render();}
async function publish(){page.status='live';await fetch('/api/pages/'+page.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(page)});alert('LIVE! See it at /live/'+page.slug);render();}
async function saveMenu(){let m=document.getElementById('inMenu').checked;let l=document.getElementById('menuLabel').value;await fetch('/api/pages/'+page.id+'/menu',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({menu:m,label:l})});}
function preview(){window.open('/live/'+page.slug)}
async function copyLink(){let link=window.location.origin+'/live/'+page.slug;navigator.clipboard.writeText(link).then(()=>alert('Copied! '+link))}
async function deletePage(){if(!confirm('Delete this whole page FOREVER? Even if LIVE, it will be gone.'))return;let r=await fetch('/api/pages/'+page.id,{method:'DELETE'});if(r.ok){alert('Page deleted');location.href='/admin'}else{alert('Could not delete')}}
render();
</script></body></html>
"""
LIVE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{page.title}}</title><style>body{margin:0;font-family:sans-serif} header{background:{{site.menu_color}};color:#fff;padding:14px 18px;display:flex;justify-content:space-between;align-items:center} .wrap{position:relative;min-height:600px;max-width:1000px;margin:0 auto} .blk{position:absolute;padding:10px} img{max-width:100%;border-radius:12px} #menu{display:none;background:#fff;color:#111;position:absolute;right:16px;top:60px;width:260px;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.2);z-index:99;padding:8px} #menu a{display:block;padding:14px;text-decoration:none;color:#111;border-bottom:1px solid #eee;font-size:17px} @media(max-width:600px){.blk{position:relative !important;left:0 !important;top:0 !important;width:100% !important}}</style></head><body>
<header><b>{{site.logo}} {{site.name}}</b><button onclick="document.getElementById('menu').style.display=document.getElementById('menu').style.display=='block'?'none':'block'" style="background:#fff;border:0;padding:10px 16px;border-radius:10px;font-size:20px">\u2630 Menu</button></header>
<div id="menu">{% for p in all_pages %}{% if p.menu and p.status=='live' %}<a href="/live/{{p.slug}}">\U0001f4c4 {{p.menu_label or p.title}}</a>{% endif %}{% endfor %}<a href="/admin">\u2699\ufe0f Admin</a></div>
<div class="wrap">{% for b in page.blocks %}<div class="blk" style="left:{{b.x}}px;top:{{b.y}}px;width:{{b.w}}px">{% if b.type=='heading' %}<h2 style="color:{{b.style.color}};font-size:{{b.style.fontSize}}px;margin:0">{{b.content}}</h2>{% elif b.type=='text' %}<p style="color:{{b.style.color}};font-size:{{b.style.fontSize}}px;margin:0">{{b.content}}</p>{% elif b.type=='image' %}<img src="{{b.content}}">{% elif b.type=='button' %}<button style="background:{{b.style.background}};color:#fff;padding:14px 22px;border-radius:10px;border:0;width:100%">{{b.content}}</button>{% elif b.type=='product' %}<div style="border:1px solid #eee;padding:14px;border-radius:12px"><b>\U0001f6cd\ufe0f {{b.content}}</b></div>{% elif b.type=='video' %}{% if 'youtube' in b.content %}<iframe width="100%" height="300" src="https://www.youtube.com/embed/{{ b.content.split('v=')[-1].split('&')[0] }}" frameborder="0" allowfullscreen></iframe>{% else %}<video controls style="width:100%;border-radius:10px"><source src="{{b.content}}"></video>{% endif %}{% elif b.type=='code' %}<div>{{b.content|safe}}</div>{% elif b.type=='divider' %}<hr>{% endif %}</div>{% endfor %}</div>
<p style="text-align:center;opacity:.5;padding:20px">\u25cf LIVE</p></body></html>
"""

LOGIN_HTML = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login - CMS</title><style>body{font-family:sans-serif;max-width:420px;margin:60px auto;padding:20px} input{width:100%;padding:14px;margin:8px 0;border:1px solid #ddd;border-radius:12px;font-size:16px} .btn{background:#111827;color:#fff;border:0;padding:14px;width:100%;border-radius:12px;font-size:16px;cursor:pointer} .box{border:1px solid #eee;padding:24px;border-radius:18px} .err{background:#fee2e2;padding:12px;border-radius:10px}</style></head><body><div class="box"><h1>Login</h1><p>{{msg}}</p>{% if err %}<div class="err">{{err}}</div>{% endif %}<form method="POST"><label>Username</label><input name="username" required><label>Password</label><input name="password" type="password" required><button class="btn">{{btn}}</button></form><p style="font-size:13px;opacity:.7">{{hint}}</p></div></body></html>
"""

def require_login():
    d = load()
    if not d.get("admin"):
        return redirect("/setup")
    if not session.get("logged_in"):
        return redirect("/login")
    return None

@app.route("/")
def home():
    d=load(); return render_template_string(ADMIN, pages=d["pages"], site=d["site"])

@app.route("/setup", methods=["GET","POST"])
def setup():
    d = load()
    if d.get("admin"):
        return redirect("/login")
    if request.method == "POST":
        u = request.form.get("username","").strip()
        pw = request.form.get("password","")
        if not u or len(pw) < 4:
            return render_template_string(LOGIN_HTML, msg="First time setup - create your admin login.", err="Username required, password 4+ characters.", btn="Create Admin Login", hint="Write this down. Delete data.json to reset.")
        d["admin"] = {"username": u, "password_hash": generate_password_hash(pw)}
        save(d)
        session["logged_in"] = True
        session["username"] = u
        return redirect("/admin")
    return render_template_string(LOGIN_HTML, msg="First time setup - create your admin login.", err="", btn="Create Admin Login", hint="Only you can edit. Visitors can still VIEW live pages without logging in.")
@app.route("/login", methods=["GET","POST"])
def login():
    d = load()
    if not d.get("admin"):
        return redirect("/setup")
    if request.method == "POST":
        u = request.form.get("username","")
        pw = request.form.get("password","")
        a = d.get("admin") or {}
        if u == a.get("username") and check_password_hash(a.get("password_hash",""), pw):
            session["logged_in"] = True
            session["username"] = u
            return redirect("/admin")
        return render_template_string(LOGIN_HTML, msg="Login to edit.", err="Wrong username or password.", btn="Log In", hint="Visitors do NOT need to log in to view live pages.")
    return render_template_string(LOGIN_HTML, msg="Login to edit.", err="", btn="Log In", hint="Visitors do NOT need to log in to view live pages.")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin")
def admin():
    r=require_login()
    if r: return r
    d=load(); return render_template_string(ADMIN, pages=d["pages"], site=d["site"])
@app.route("/builder/<pid>")
def builder(pid):
    r=require_login()
    if r: return r
    d=load(); p=next((x for x in d["pages"] if x["id"]==pid), None)
    if not p: return "Not found",404
    return render_template_string(BUILDER, page=p)
@app.route("/live/<slug>")
def live(slug):
    d=load(); p=next((x for x in d["pages"] if x["slug"]==slug and x["status"]=="live"), None)
    if not p: return "<h1>Not live yet. Publish it in Builder.</h1><a href='/admin'>Back</a>",404
    return render_template_string(LIVE, page=p, all_pages=d["pages"], site=d["site"])
@app.route("/api/pages", methods=["GET","POST"])
def api_pages():
    r=require_login()
    if r: return r
    d=load()
    if request.method=="POST":
        j=request.json; t=j.get("title","Untitled")
        new={"id":str(uuid.uuid4())[:8],"title":t,"slug":t.lower().replace(" ","-"),"status":"draft","menu":True,"menu_label":t,"updated":datetime.now().strftime("%Y-%m-%d"),"blocks":[]}
        d["pages"].append(new); save(d); return jsonify(new)
    return jsonify(d["pages"])
@app.route("/api/pages/<pid>", methods=["PUT","DELETE"])
def api_page(pid):
    r=require_login()
    if r: return r
    d=load(); p=next((x for x in d["pages"] if x["id"]==pid), None)
    if not p: return jsonify({"error":"not found"}),404
    if request.method=="PUT":
        j=request.json; p.update({k:v for k,v in j.items() if k in ["title","slug","status","blocks","menu","menu_label"]}); save(d); return jsonify(p)
    # DELETE works for DRAFT and LIVE - no status check
    d["pages"]=[x for x in d["pages"] if x["id"]!=pid]; save(d); return jsonify({"ok":True, "deleted": pid})
@app.route("/api/pages/<pid>/menu", methods=["POST"])
def api_menu(pid):
    r=require_login()
    if r: return r
    d=load(); p=next((x for x in d["pages"] if x["id"]==pid), None)
    if not p: return jsonify({"error":"not found"}),404
    j=request.json
    if "menu" in j: p["menu"]=j["menu"]
    if "label" in j: p["menu_label"]=j["label"]
    save(d); return jsonify(p)

@app.route("/api/upload", methods=["POST"])
def upload():
    r=require_login()
    if r: return r
    if "file" not in request.files:
        return jsonify({"error":"no file"}),400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error":"no file"}),400
    fn = secure_filename(f.filename)
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ALLOWED_VIDEO and ext not in {".jpg",".jpeg",".png",".gif",".webp"}:
        return jsonify({"error":"Only video + image files allowed"}),400
    fn = str(uuid.uuid4())[:8] + "_" + fn
    f.save(os.path.join(app.config["UPLOAD_FOLDER"], fn))
    return jsonify({"url": "/static/uploads/" + fn})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
