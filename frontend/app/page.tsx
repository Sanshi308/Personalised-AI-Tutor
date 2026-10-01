"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, BookOpen, Brain, CheckCircle2, ChevronRight, CircleHelp, Gauge, GraduationCap, LayoutDashboard, MessageSquare, RefreshCw, Sparkles, Target, Trophy, UserRound } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Profile = { name: string; level: string; streak: number };
type Stats = { name: string; level: string; avg_score: number; quizzes: number; weak_topic: {topic:string;score:number;attempts:number}; topics: {topic:string;score:number;attempts:number}[]; recent:any[] };
type Question = { question:string; options:string[]; answer:number; explanation:string };

const topics = ["Machine Learning", "Linear Regression", "Gradient Descent", "Neural Networks", "Classification", "Overfitting", "Decision Trees"];

export default function Home() {
  const [page, setPage] = useState("dashboard");
  const [profile, setProfile] = useState<Profile>({name:"Learner", level:"Beginner", streak:0});
  const [stats, setStats] = useState<Stats | null>(null);
  const [topic, setTopic] = useState("Gradient Descent");
  const [chat, setChat] = useState<{role:string;text:string}[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [quiz, setQuiz] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function refresh() {
    try {
      const [p, s] = await Promise.all([fetch(`${API}/api/profile`), fetch(`${API}/api/stats`)]);
      setProfile(await p.json());
      setStats(await s.json());
    } catch {}
  }
  useEffect(() => { refresh(); }, []);

  const greeting = useMemo(() => {
    const h = new Date().getHours();
    return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  }, []);

  async function ask(action="explain", custom?:string) {
    const text = custom ?? message;
    if (!text.trim()) return;
    setBusy(true);
    setChat(c => [...c, {role:"user", text}]);
    setMessage("");
    try {
      const r = await fetch(`${API}/api/tutor`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({
        message:text, topic, level:profile.level, action, recent_performance:stats?.topics || []
      })});
      const data = await r.json();
      setChat(c => [...c, {role:"assistant", text:data.answer || data.detail || "Please try again."}]);
    } catch {
      setChat(c => [...c, {role:"assistant", text:"Backend is not running. Start FastAPI on port 8000 and try again."}]);
    } finally { setBusy(false); }
  }

  async function makeQuiz() {
    setPage("quiz"); setBusy(true); setQuiz([]); setAnswers([]); setSubmitted(false); setResult(null);
    try {
      const r = await fetch(`${API}/api/quiz`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({topic,level:profile.level})});
      const data = await r.json(); setQuiz(data.questions || []);
    } catch {}
    finally { setBusy(false); }
  }

  async function submitQuiz() {
    const score = quiz.reduce((n,q,i) => n + (answers[i] === q.answer ? 1 : 0), 0);
    setSubmitted(true);
    const r = await fetch(`${API}/api/quiz/submit`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({topic,level:profile.level,score,total:quiz.length})});
    setResult(await r.json()); refresh();
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="logo"><Sparkles size={20}/></div><div><b>Vector Tutor</b><span>AI Learning Companion</span></div></div>
        <div className="profile-mini"><div className="avatar">{profile.name.slice(0,1).toUpperCase()}</div><div><b>{profile.name}</b><span>{profile.level} learner</span></div></div>
        <nav>
          <Nav active={page==="dashboard"} icon={<LayoutDashboard size={18}/>} text="Dashboard" onClick={()=>setPage("dashboard")}/>
          <Nav active={page==="tutor"} icon={<MessageSquare size={18}/>} text="AI Tutor" onClick={()=>setPage("tutor")}/>
          <Nav active={page==="quiz"} icon={<CircleHelp size={18}/>} text="Practice Quiz" onClick={makeQuiz}/>
          <Nav active={page==="progress"} icon={<Gauge size={18}/>} text="Progress" onClick={()=>setPage("progress")}/>
        </nav>
        <div className="sidebar-bottom"><div className="tiny-label">LEARNING LOOP</div><div className="loop">Learn <ChevronRight size={14}/> Practice <ChevronRight size={14}/> Diagnose <ChevronRight size={14}/> Adapt</div></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><span className="eyebrow">PERSONALISED LEARNING</span><h1>{page === "dashboard" ? `${greeting}, ${profile.name} 👋` : page === "tutor" ? "AI Tutor" : page === "quiz" ? "Practice Lab" : "Your Progress"}</h1></div>
          <div className="level-select"><span>Learning level</span><select value={profile.level} onChange={async e=>{const level=e.target.value; setProfile({...profile,level}); await fetch(`${API}/api/profile`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:profile.name,level})});}}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
        </header>

        {page==="dashboard" && <Dashboard stats={stats} topic={topic} setTopic={setTopic} setPage={setPage} makeQuiz={makeQuiz}/>}
        {page==="tutor" && <Tutor topic={topic} setTopic={setTopic} chat={chat} message={message} setMessage={setMessage} ask={ask} busy={busy}/>}
        {page==="quiz" && <Quiz topic={topic} setTopic={setTopic} quiz={quiz} answers={answers} setAnswers={setAnswers} submitted={submitted} result={result} submitQuiz={submitQuiz} makeQuiz={makeQuiz} busy={busy}/>}
        {page==="progress" && <Progress stats={stats}/>}
      </main>
    </div>
  );
}

function Nav({active,icon,text,onClick}:{active:boolean;icon:any;text:string;onClick:()=>void}) {
  return <button className={`nav ${active?"active":""}`} onClick={onClick}>{icon}<span>{text}</span>{active&&<span className="dot"/>}</button>
}

function Dashboard({stats,topic,setTopic,setPage,makeQuiz}:{stats:Stats|null;topic:string;setTopic:(s:string)=>void;setPage:(s:string)=>void;makeQuiz:()=>void}) {
  return <div className="content">
    <section className="hero">
      <div><div className="pill"><Sparkles size={14}/> Adaptive learning enabled</div><h2>Learn AI at <em>your pace.</em></h2><p>Ask questions, practise what you learn, and get your next best learning step from your recent performance.</p>
      <div className="hero-actions"><button className="primary" onClick={()=>setPage("tutor")}><MessageSquare size={17}/> Start learning</button><button className="secondary" onClick={makeQuiz}><CircleHelp size={17}/> Quiz me</button></div></div>
      <div className="hero-art"><Brain size={54}/><span>Learn → Practice → Improve</span></div>
    </section>

    <div className="grid4">
      <Metric icon={<Trophy/>} label="Average score" value={`${stats?.avg_score ?? 0}%`} sub="Across your quizzes"/>
      <Metric icon={<BookOpen/>} label="Quizzes completed" value={`${stats?.quizzes ?? 0}`} sub="Keep practising"/>
      <Metric icon={<Target/>} label="Focus topic" value={stats?.weak_topic?.topic || "Gradient Descent"} sub={stats?.weak_topic?.score ? `${stats.weak_topic.score}% recent score` : "Start your first quiz"}/>
      <Metric icon={<CheckCircle2/>} label="Learning mode" value="Adaptive" sub="Level-aware tutor"/>
    </div>

    <section className="two-col">
      <div className="card">
        <div className="card-head"><div><span className="eyebrow">RECOMMENDED NEXT</span><h3>Build confidence in {stats?.weak_topic?.topic || "Gradient Descent"}</h3></div><Target className="head-icon"/></div>
        <p className="muted">Based on your recent performance, review the core idea first, then test yourself with a fresh question set.</p>
        <div className="recommend"><div className="rec-num">01</div><div><b>Understand the concept</b><span>Get a level-matched explanation with an example.</span></div></div>
        <div className="recommend"><div className="rec-num">02</div><div><b>Practise retrieval</b><span>Answer five questions without looking at notes.</span></div></div>
        <button className="text-btn" onClick={()=>setPage("tutor")}>Open personalised lesson <ChevronRight size={16}/></button>
      </div>
      <div className="card">
        <div className="card-head"><div><span className="eyebrow">TOPICS</span><h3>Choose what to learn</h3></div></div>
        <div className="topic-list">{topics.map(t=><button key={t} className={topic===t?"topic active-topic":"topic"} onClick={()=>setTopic(t)}><span>{t}</span><ChevronRight size={15}/></button>)}</div>
      </div>
    </section>
  </div>
}

function Metric({icon,label,value,sub}:{icon:any;label:string;value:string;sub:string}) {
  return <div className="metric"><div className="metric-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>
}

function Tutor({topic,setTopic,chat,message,setMessage,ask,busy}:{topic:string;setTopic:(s:string)=>void;chat:any[];message:string;setMessage:(s:string)=>void;ask:(a?:string,c?:string)=>void;busy:boolean}) {
  return <div className="content tutor-page">
    <div className="topicbar"><span>TOPIC</span><select value={topic} onChange={e=>setTopic(e.target.value)}>{topics.map(t=><option key={t}>{t}</option>)}</select><span className="secure">✦ Level-aware responses</span></div>
    <div className="chat-card">
      <div className="chat-head"><div className="bot"><Bot size={20}/></div><div><b>Vector Tutor</b><span>Personalised AI tutor</span></div><div className="online">● Online</div></div>
      <div className="chat-body">
        {chat.length===0 && <div className="welcome"><div className="welcome-icon"><GraduationCap size={28}/></div><h2>What would you like to understand?</h2><p>Ask me about {topic}. I will adapt the explanation to your selected level.</p><div className="suggestions"><button onClick={()=>ask("explain",`Explain ${topic} like I’m a beginner.`)}>Explain simply</button><button onClick={()=>ask("example",`Give me a practical example of ${topic}.`)}>Give an example</button><button onClick={()=>ask("simpler",`Explain ${topic} even more simply.`)}>Explain simpler</button></div></div>}
        {chat.map((m,i)=><div key={i} className={`bubble-row ${m.role==="user"?"user":""}`}><div className={`bubble ${m.role==="user"?"user-bubble":"ai-bubble"}`}>{m.text}</div></div>)}
        {busy && <div className="typing"><span/><span/><span/> Tutor is thinking…</div>}
      </div>
      <div className="quick"><button onClick={()=>ask("simpler","Explain that more simply.")}>Explain simpler</button><button onClick={()=>ask("example","Give me a practical example.")}>Give example</button><button onClick={()=>ask("explain","Quiz me on this topic.")}>Quiz me</button></div>
      <div className="composer"><input value={message} onChange={e=>setMessage(e.target.value)} onKeyDown={e=>e.key==="Enter"&&ask()} placeholder={`Ask anything about ${topic}…`}/><button onClick={()=>ask()} disabled={busy}><ChevronRight/></button></div>
    </div>
  </div>
}

function Quiz({topic,setTopic,quiz,answers,setAnswers,submitted,result,submitQuiz,makeQuiz,busy}:{topic:string;setTopic:(s:string)=>void;quiz:Question[];answers:number[];setAnswers:(a:number[])=>void;submitted:boolean;result:any;submitQuiz:()=>void;makeQuiz:()=>void;busy:boolean}) {
  return <div className="content">
    <div className="quiz-toolbar"><div><span className="eyebrow">PRACTICE LAB</span><h2>Test your understanding</h2><p className="muted">Five questions generated for your level and selected topic.</p></div><select value={topic} onChange={e=>setTopic(e.target.value)}>{topics.map(t=><option key={t}>{t}</option>)}</select></div>
    {busy && <div className="card loading"><RefreshCw className="spin"/> Generating your personalised quiz…</div>}
    {!busy && quiz.length===0 && <div className="empty card"><CircleHelp size={38}/><h3>Ready when you are</h3><p>Generate five questions for {topic}.</p><button className="primary" onClick={makeQuiz}>Generate quiz</button></div>}
    {!busy && quiz.length>0 && <div className="quiz-list">{quiz.map((q,i)=><div className="question card" key={i}><div className="q-top"><span>QUESTION {String(i+1).padStart(2,"0")}</span><b>{answers[i]!==undefined ? "Answered" : "Not answered"}</b></div><h3>{q.question}</h3><div className="options">{q.options.map((o,j)=><button key={j} disabled={submitted} className={`option ${answers[i]===j?"selected":""} ${submitted&&j===q.answer?"correct":""} ${submitted&&answers[i]===j&&j!==q.answer?"wrong":""}`} onClick={()=>{const a=[...answers];a[i]=j;setAnswers(a)}}><span>{String.fromCharCode(65+j)}</span>{o}</button>)}</div>{submitted&&<div className="explanation"><b>Why:</b> {q.explanation}</div>}</div>)}{!submitted?<button className="primary submit" onClick={submitQuiz}>Submit & diagnose <ChevronRight size={17}/></button>:<div className="result card"><div className="result-score">{result?.percentage}%</div><div><span className="eyebrow">YOUR RESULT</span><h2>{result?.score}/{result?.total} correct</h2><p>{result?.recommendation}</p></div><button className="secondary" onClick={makeQuiz}>Try another set</button></div>}</div>}
  </div>
}

function Progress({stats}:{stats:Stats|null}) {
  return <div className="content"><div className="progress-grid"><div className="card big-progress"><span className="eyebrow">LEARNING SNAPSHOT</span><h2>{stats?.avg_score ?? 0}%</h2><p>Average quiz score</p><div className="bar"><i style={{width:`${stats?.avg_score ?? 0}%`}}/></div><div className="stat-line"><span>Quizzes completed</span><b>{stats?.quizzes ?? 0}</b></div><div className="stat-line"><span>Current level</span><b>{stats?.level ?? "Beginner"}</b></div></div><div className="card"><span className="eyebrow">TOPIC MASTERY</span><h3>Where to focus next</h3>{(stats?.topics?.length?stats.topics:[{topic:"Take a quiz to unlock",score:0,attempts:0}]).map((t,i)=><div className="mastery" key={i}><div><span>{t.topic}</span><b>{t.score}%</b></div><div className="bar"><i style={{width:`${t.score}%`}}/></div></div>)}</div></div></div>
}
