import { useState, useCallback, useEffect } from "react";
import axios from "axios";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import "./App.css";

const API = "/api";
const scoreColor = (s) => s >= 75 ? "#16a34a" : s >= 50 ? "#f59e0b" : "#dc2626";
const scoreBg    = (s) => s >= 75 ? "#dcfce7" : s >= 50 ? "#fef3c7" : "#fee2e2";

const LOADING_STEPS = [
  "📄 Reading your resume...",
  "🔍 Scanning job description...",
  "🧠 Matching skills with AI...",
  "✍️  Generating AI feedback...",
  "📊 Calculating ATS score...",
];

export default function App() {
  const [dark,           setDark]           = useState(false);
  const [resume,         setResume]         = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [candidateName,  setCandidateName]  = useState("");
  const [result,         setResult]         = useState(null);
  const [loading,        setLoading]        = useState(false);
  const [downloading,    setDownloading]    = useState(false);

  // Cover letter
  const [coverLoading,   setCoverLoading]   = useState(false);
  const [coverLetter,    setCoverLetter]    = useState("");
  const [showCover,      setShowCover]      = useState(false);
  const [coverPdfLoading, setCoverPdfLoading] = useState(false);

  // Interview questions
  const [qLoading,       setQLoading]       = useState(false);
  const [questions,      setQuestions]      = useState([]);
  const [showQuestions,  setShowQuestions]  = useState(false);

  // Bullet rewriter
  const [rwLoading,      setRwLoading]      = useState(false);
  const [rewrites,       setRewrites]       = useState([]);
  const [showRewrites,   setShowRewrites]   = useState(false);

  const [showAllMatched, setShowAllMatched] = useState(false);
  const [showAllMissing, setShowAllMissing] = useState(false);
  const [dragOver,       setDragOver]       = useState(false);
  const [error,          setError]          = useState("");
  const [stepIdx,        setStepIdx]        = useState(0);
  const [displayScore,   setDisplayScore]   = useState(0);

  useEffect(() => {
    document.body.className = dark ? "dark-body" : "";
  }, [dark]);

  useEffect(() => {
    if (!loading) return;
    const t = setInterval(() => setStepIdx(i => (i + 1) % LOADING_STEPS.length), 1800);
    return () => clearInterval(t);
  }, [loading]);

  useEffect(() => {
    if (!result) return;
    setDisplayScore(0);
    const target = result["ATS Score"];
    let cur = 0;
    const t = setInterval(() => {
      cur += 1;
      setDisplayScore(cur);
      if (cur >= target) clearInterval(t);
    }, 18);
    return () => clearInterval(t);
  }, [result]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === "application/pdf") { setResume(file); setError(""); }
    else setError("Please drop a PDF file only.");
  }, []);

  const resetAllFeatures = () => {
    setCoverLetter(""); setShowCover(false);
    setQuestions([]); setShowQuestions(false);
    setRewrites([]); setShowRewrites(false);
  };

  // ── Calculate ATS ────────────────────────────────────────
  const calculateATS = async () => {
    if (!resume)              return setError("Please upload your resume.");
    if (!jobDescription.trim()) return setError("Please paste the Job Description.");
    setError(""); setResult(null); resetAllFeatures();
    const fd = new FormData();
    fd.append("resume", resume);
    fd.append("job_description", jobDescription);
    try {
      setLoading(true);
      const { data } = await axios.post(`${API}/calculate-ats/`, fd);
      setResult(data);
      setShowAllMatched(false);
      setShowAllMissing(false);
    } catch {
      setError("Cannot connect to backend. Make sure FastAPI is running: uvicorn app.main:app --reload");
    } finally {
      setLoading(false);
    }
  };

  // ── Download Full PDF Report ─────────────────────────────
  const downloadPDF = async () => {
    if (!resume) return setError("Please upload resume first.");
    if (!result) return setError("Please calculate ATS score first.");
    const fd = new FormData();
    fd.append("resume", resume);
    fd.append("job_description", jobDescription);
    fd.append("candidate_name", candidateName || "Candidate");
    try {
      setDownloading(true);
      setError("");
      const resp = await fetch(`${API}/download-pdf/`, { method: "POST", body: fd });
      if (!resp.ok) { setError("PDF generation failed."); return; }
      const blob = await resp.blob();
      if (blob.size < 100) { setError("PDF is empty."); return; }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ResumeIQ_${(candidateName || "Report").replace(/ /g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
    } catch (err) {
      setError("PDF download failed: " + err.message);
    } finally {
      setDownloading(false);
    }
  };

  // ── FEATURE: Cover Letter (generate text) ────────────────
  const generateCoverLetter = async () => {
    if (!resume || !jobDescription.trim()) return;
    const fd = new FormData();
    fd.append("resume", resume);
    fd.append("job_description", jobDescription);
    fd.append("candidate_name", candidateName || "Candidate");
    try {
      setCoverLoading(true);
      const { data } = await axios.post(`${API}/generate-cover-letter/`, fd);
      setCoverLetter(data.cover_letter);
      setShowCover(true);
    } catch {
      setError("Cover letter generation failed.");
    } finally {
      setCoverLoading(false);
    }
  };

  // ── FEATURE 1: Download Cover Letter as PDF ──────────────
  const downloadCoverLetterPDF = async () => {
    if (!coverLetter) return;
    const fd = new FormData();
    fd.append("cover_letter", coverLetter);
    fd.append("candidate_name", candidateName || "Candidate");
    try {
      setCoverPdfLoading(true);
      const resp = await fetch(`${API}/download-cover-letter-pdf/`, { method: "POST", body: fd });
      if (!resp.ok) { setError("Cover letter PDF failed."); return; }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `CoverLetter_${(candidateName || "Report").replace(/ /g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
    } catch (err) {
      setError("Cover letter PDF download failed.");
    } finally {
      setCoverPdfLoading(false);
    }
  };

  // ── FEATURE 2: Interview Question Generator ──────────────
  const generateQuestions = async () => {
    if (!jobDescription.trim()) return setError("Please paste a Job Description first.");
    const fd = new FormData();
    fd.append("job_description", jobDescription);
    try {
      setQLoading(true);
      setError("");
      const { data } = await axios.post(`${API}/interview-questions/`, fd);
      setQuestions(data.questions || []);
      setShowQuestions(true);
    } catch {
      setError("Could not generate interview questions.");
    } finally {
      setQLoading(false);
    }
  };

  // ── FEATURE 3: Resume Bullet Rewriter ────────────────────
  const generateRewrites = async () => {
    if (!resume || !jobDescription.trim()) return setError("Upload resume and paste JD first.");
    const fd = new FormData();
    fd.append("resume", resume);
    fd.append("job_description", jobDescription);
    try {
      setRwLoading(true);
      setError("");
      const { data } = await axios.post(`${API}/rewrite-bullets/`, fd);
      setRewrites(data.rewrites || []);
      setShowRewrites(true);
    } catch {
      setError("Could not generate rewrite suggestions.");
    } finally {
      setRwLoading(false);
    }
  };

  const pieData = result ? [
    { name: "ATS Score",     value: result["ATS Score"] },
    { name: "Skill Match",   value: result["Skill Match"] },
    { name: "Section Score", value: result["Resume Analysis"]?.["Section Score"] || 0 },
  ] : [];
  const PIE_COLORS = ["#2563eb", "#16a34a", "#f59e0b"];

  return (
    <div className={`app-wrapper ${dark ? "dark" : ""}`}>

      <header className="header">
        <div className="header-inner">
          <h1>🚀 ResumeIQ AI</h1>
          <p>AI-powered ATS resume analyser — built by <strong>Shyama Mishra</strong></p>
        </div>
        <button className="dark-toggle" onClick={() => setDark(!dark)}>
          {dark ? "☀️ Light" : "🌙 Dark"}
        </button>
      </header>

      <main className="main">

        <section className="card input-card">
          <h2>📤 Upload & Analyse</h2>

          <label className="field-label">Your Name (for PDF report)</label>
          <input
            className="text-input"
            type="text"
            placeholder="e.g. Shyama Mishra"
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
          />

          <label className="field-label">Resume (PDF)</label>
          <div
            className={`drop-zone ${dragOver ? "drag-active" : ""} ${resume ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => document.getElementById("file-input").click()}
          >
            {resume ? (
              <div className="file-info">
                <span className="file-icon">📄</span>
                <div>
                  <p className="file-name">{resume.name}</p>
                  <p className="file-meta">{(resume.size / 1024).toFixed(1)} KB · PDF</p>
                </div>
                <span className="file-ok">✅ Ready</span>
              </div>
            ) : (
              <div className="drop-hint">
                <span className="drop-icon">☁️</span>
                <p>Drag & drop your PDF here</p>
                <p className="drop-sub">or click to browse</p>
              </div>
            )}
          </div>
          <input id="file-input" type="file" accept=".pdf" style={{ display: "none" }}
            onChange={(e) => { setResume(e.target.files[0]); setError(""); }} />

          <label className="field-label">Job Description</label>
          <textarea
            className="jd-textarea" rows={9}
            placeholder="Paste the full Job Description here…"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />

          {error && <p className="error-msg">⚠️ {error}</p>}

          <button className="btn-primary" onClick={calculateATS} disabled={loading}>
            {loading
              ? <span className="btn-loading"><span className="spinner" /> Analysing…</span>
              : "⚡ Calculate ATS Score"}
          </button>
        </section>

        {loading && (
          <div className="loading-card">
            <div className="big-spinner" />
            <p className="loading-step">{LOADING_STEPS[stepIdx]}</p>
            <p className="loading-sub">AI is working… takes 10–20 seconds</p>
          </div>
        )}

        {result && !loading && (
          <section className="results">

            <div className="score-banner" style={{
              background: scoreBg(result["ATS Score"]),
              borderLeft: `5px solid ${scoreColor(result["ATS Score"])}`,
            }}>
              <span style={{ color: scoreColor(result["ATS Score"]), fontSize: "1.1rem", fontWeight: 700 }}>
                {result["ATS Score"] >= 75 ? "🎉 Strong candidate for this role!"
                  : result["ATS Score"] >= 50 ? "⚠️ Good fit — a few gaps to address"
                  : "❌ Resume needs significant tailoring for this role"}
              </span>
            </div>

            <div className="dashboard-grid">
              {[
                { icon: "🎯", label: "ATS Score",     val: `${result["ATS Score"]}%`,     color: scoreColor(result["ATS Score"]),   bg: scoreBg(result["ATS Score"]) },
                { icon: "🧠", label: "Skill Match",    val: `${result["Skill Match"]}%`,    color: scoreColor(result["Skill Match"]),  bg: scoreBg(result["Skill Match"]) },
                { icon: "📄", label: "Resume Length",  val: result["Resume Length"],        color: "#2563eb", bg: "#eff6ff" },
                { icon: "❌", label: "Missing Skills", val: result["Missing Skills"].length, color: "#dc2626", bg: "#fee2e2" },
              ].map(({ icon, label, val, color, bg }) => (
                <div className="stat-card" key={label} style={{ background: bg, borderColor: color + "44" }}>
                  <span className="stat-icon">{icon}</span>
                  <p className="stat-label">{label}</p>
                  <p className="stat-value" style={{ color }}>{val}</p>
                </div>
              ))}
            </div>

            <div className="chart-row">
              <div className="card chart-card">
                <h3>Overall ATS Score</h3>
                <div className="circular-wrap">
                  <CircularProgressbar
                    value={displayScore}
                    text={`${displayScore}%`}
                    styles={buildStyles({
                      textSize: "16px",
                      pathColor:  scoreColor(result["ATS Score"]),
                      textColor:  dark ? "#f1f5f9" : "#111827",
                      trailColor: dark ? "#334155" : "#e5e7eb",
                    })}
                  />
                </div>
                <p className="status-msg">{result["Message"]}</p>
              </div>
              <div className="card chart-card">
                <h3>Score Breakdown</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                      {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => `${v}%`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="skills-row">
              <div className="card skill-card">
                <h3>✅ Matched Skills <span className="count-badge green">{result["Matched Skills"].length}</span></h3>
                <div className="badge-wrap">
                  {(showAllMatched ? result["Matched Skills"] : result["Matched Skills"].slice(0, 8))
                    .map((s) => <span key={s} className="badge matched">{s}</span>)}
                </div>
                {result["Matched Skills"].length > 8 && (
                  <button className="show-more" onClick={() => setShowAllMatched(!showAllMatched)}>
                    {showAllMatched ? "Show Less ▲" : `Show ${result["Matched Skills"].length - 8} More ▼`}
                  </button>
                )}
              </div>
              <div className="card skill-card">
                <h3>❌ Missing Skills <span className="count-badge red">{result["Missing Skills"].length}</span></h3>
                <div className="badge-wrap">
                  {(showAllMissing ? result["Missing Skills"] : result["Missing Skills"].slice(0, 8))
                    .map((s) => <span key={s} className="badge missing">{s}</span>)}
                </div>
                {result["Missing Skills"].length > 8 && (
                  <button className="show-more" onClick={() => setShowAllMissing(!showAllMissing)}>
                    {showAllMissing ? "Show Less ▲" : `Show ${result["Missing Skills"].length - 8} More ▼`}
                  </button>
                )}
              </div>
            </div>

            <div className="card">
              <h3>💡 Suggestions</h3>
              <ul className="tip-list">
                {result["Suggestions"].map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>

            <div className="card ai-card">
              <h3>🤖 AI Resume Feedback <span className="ai-tag">LLaMA 3.3 70B</span></h3>
              <ul className="tip-list ai-tips">
                {result["AI Feedback"].map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>

            {result["Resume Analysis"] && (
              <div className="card">
                <h3>📋 Section Analysis
                  <span className="section-score" style={{ color: scoreColor(result["Resume Analysis"]["Section Score"]) }}>
                    {result["Resume Analysis"]["Section Score"]}%
                  </span>
                </h3>
                <div className="section-grid">
                  <div>
                    <p className="section-sub green-text">✅ Found</p>
                    <ul className="section-list">
                      {result["Resume Analysis"]["Found Sections"].map(s => <li key={s}>{s}</li>)}
                    </ul>
                  </div>
                  <div>
                    <p className="section-sub red-text">❌ Missing</p>
                    <ul className="section-list">
                      {result["Resume Analysis"]["Missing Sections"].length
                        ? result["Resume Analysis"]["Missing Sections"].map(s => <li key={s}>{s}</li>)
                        : <li>None 🎉</li>}
                    </ul>
                  </div>
                </div>
                {result["Resume Analysis"]["Section Suggestions"].length > 0 && (
                  <ul className="tip-list" style={{ marginTop: 12 }}>
                    {result["Resume Analysis"]["Section Suggestions"].map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                )}
              </div>
            )}

            {/* ── FEATURE 1: Cover Letter ── */}
            <div className="card ai-card cover-card">
              <h3>✉️ AI Cover Letter Generator <span className="ai-tag">LLaMA 3.3 70B</span></h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "12px" }}>
                Generate a personalised cover letter based on your resume + this JD.
              </p>
              <button className="btn-cover" onClick={generateCoverLetter} disabled={coverLoading}>
                {coverLoading
                  ? <span className="btn-loading"><span className="spinner" /> Generating…</span>
                  : "✨ Generate Cover Letter"}
              </button>
              {showCover && coverLetter && (
                <div className="cover-output">
                  <pre className="cover-text">{coverLetter}</pre>
                  <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                    <button className="copy-btn" onClick={() => navigator.clipboard.writeText(coverLetter)}>
                      📋 Copy to Clipboard
                    </button>
                    <button className="copy-btn" onClick={downloadCoverLetterPDF} disabled={coverPdfLoading}>
                      {coverPdfLoading ? "Generating…" : "📥 Download as PDF"}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* ── FEATURE 2: Interview Questions ── */}
            <div className="card ai-card questions-card">
              <h3>❓ AI Interview Question Generator <span className="ai-tag">LLaMA 3.3 70B</span></h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "12px" }}>
                Generate 10 likely interview questions based on this Job Description.
              </p>
              <button className="btn-cover" onClick={generateQuestions} disabled={qLoading}>
                {qLoading
                  ? <span className="btn-loading"><span className="spinner" /> Generating…</span>
                  : "🎯 Generate Interview Questions"}
              </button>
              {showQuestions && questions.length > 0 && (
                <div className="questions-output">
                  {questions.map((q, i) => (
                    <div key={i} className="question-item">
                      <span className={`q-type ${q.type === "Technical" ? "q-tech" : "q-hr"}`}>{q.type}</span>
                      <p>{q.question}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* ── FEATURE 3: Bullet Rewriter ── */}
            <div className="card ai-card rewrite-card">
              <h3>✍️ Resume Bullet Rewriter <span className="ai-tag">LLaMA 3.3 70B</span></h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "12px" }}>
                See exactly how to rewrite your resume bullets to better match this JD.
              </p>
              <button className="btn-cover" onClick={generateRewrites} disabled={rwLoading}>
                {rwLoading
                  ? <span className="btn-loading"><span className="spinner" /> Analysing…</span>
                  : "🔄 Generate Rewrite Suggestions"}
              </button>
              {showRewrites && rewrites.length > 0 && (
                <div className="rewrites-output">
                  {rewrites.map((r, i) => (
                    <div key={i} className="rewrite-item">
                      <div className="rewrite-before">
                        <span className="rewrite-label">BEFORE</span>
                        <p>{r.before}</p>
                      </div>
                      <div className="rewrite-arrow">→</div>
                      <div className="rewrite-after">
                        <span className="rewrite-label">AFTER</span>
                        <p>{r.after}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button className="btn-download" onClick={downloadPDF} disabled={downloading}>
              {downloading
                ? <span className="btn-loading"><span className="spinner white" /> Generating PDF…</span>
                : "📥 Download Full PDF Report"}
            </button>

          </section>
        )}
      </main>

      <footer className="footer">
        <p>🚀 <strong>ResumeIQ AI</strong> · Built by <strong>Shyama Mishra</strong> · B.Tech CSE Data Science, Galgotias 2027</p>
        <p>Powered by LLaMA 3.3 70B · Groq · FastAPI · React · TF-IDF NLP</p>
      </footer>
    </div>
  );
}
