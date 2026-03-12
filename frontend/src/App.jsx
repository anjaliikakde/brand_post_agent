import { useState } from "react";

const API_BASE = "http://localhost:8000";

// Stable brand ID for this session — scopes all uploads + RAG to one namespace
const SESSION_BRAND_ID = "brand_" + Math.random().toString(36).slice(2, 10);

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --cream: #FAF8F4;
    --ink: #1A1714;
    --muted: #8A847C;
    --accent: #D4622A;
    --accent-light: #F5E6DC;
    --border: #E8E3DB;
    --card: #FFFFFF;
    --success: #2E7D4F;
    --radius: 16px;
  }

  body { font-family: 'DM Sans', sans-serif; background: var(--cream); color: var(--ink); min-height: 100vh; }

  .app { max-width: 720px; margin: 0 auto; padding: 48px 24px 80px; }

  .header { margin-bottom: 48px; }

  .header-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--accent); background: var(--accent-light); padding: 5px 12px;
    border-radius: 100px; margin-bottom: 16px;
  }

  .header-eyebrow::before {
    content: ''; width: 6px; height: 6px; background: var(--accent);
    border-radius: 50%; animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }

  .header h1 {
    font-family: 'Instrument Serif', serif;
    font-size: clamp(36px, 6vw, 52px); font-weight: 400; line-height: 1.1; letter-spacing: -0.02em;
  }

  .header h1 em { font-style: italic; color: var(--accent); }

  .header p { margin-top: 12px; font-size: 15px; color: var(--muted); font-weight: 300; line-height: 1.6; }

  .steps { display: flex; align-items: center; margin-bottom: 32px; }

  .step-item {
    display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 500;
    color: var(--muted); letter-spacing: 0.02em; white-space: nowrap;
  }

  .step-item.active { color: var(--ink); }
  .step-item.done { color: var(--success); }

  .step-num {
    width: 24px; height: 24px; border-radius: 50%; border: 1.5px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 500; flex-shrink: 0; transition: all 0.2s;
  }

  .step-item.active .step-num { border-color: var(--accent); background: var(--accent); color: white; }
  .step-item.done .step-num { border-color: var(--success); background: var(--success); color: white; }
  .step-line { flex: 1; height: 1px; background: var(--border); margin: 0 10px; }

  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 32px; margin-bottom: 16px; transition: box-shadow 0.2s ease;
  }

  .card:hover { box-shadow: 0 4px 24px rgba(26,23,20,0.06); }

  .card-label { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }

  textarea, input[type="text"] {
    width: 100%; font-family: 'DM Sans', sans-serif; font-size: 15px; font-weight: 300;
    color: var(--ink); background: transparent; border: none; outline: none;
    resize: none; line-height: 1.7; caret-color: var(--accent);
  }

  textarea::placeholder, input::placeholder { color: var(--border); }

  .input-row { display: flex; gap: 12px; align-items: flex-start; }

  .input-icon {
    width: 32px; height: 32px; border-radius: 8px; background: var(--accent-light);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px; font-size: 14px;
  }

  .divider { height: 1px; background: var(--border); margin: 20px 0; }

  .upload-zone {
    border: 1.5px dashed var(--border); border-radius: 12px; padding: 32px 24px;
    text-align: center; cursor: pointer; transition: all 0.2s ease; position: relative;
  }

  .upload-zone:hover, .upload-zone.drag-over { border-color: var(--accent); background: var(--accent-light); }

  .upload-zone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }

  .upload-icon { font-size: 28px; margin-bottom: 10px; display: block; }
  .upload-title { font-size: 14px; font-weight: 500; color: var(--ink); margin-bottom: 4px; }
  .upload-sub { font-size: 12px; color: var(--muted); }
  .upload-sub span { color: var(--accent); font-weight: 500; }

  .file-list { display: flex; flex-direction: column; gap: 8px; margin-top: 14px; }

  .file-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; background: var(--cream); border-radius: 10px;
    border: 1px solid var(--border); animation: fadeUp 0.2s ease;
  }

  .file-item-left { display: flex; align-items: center; gap: 10px; min-width: 0; }

  .file-item-icon {
    width: 32px; height: 32px; border-radius: 8px; background: var(--accent-light);
    display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
  }

  .file-item-name { font-size: 13px; font-weight: 500; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 280px; }
  .file-item-size { font-size: 11px; color: var(--muted); margin-top: 1px; }

  .file-status { display: flex; align-items: center; gap: 6px; font-size: 12px; flex-shrink: 0; }
  .file-status.uploading { color: var(--accent); }
  .file-status.done { color: var(--success); }
  .file-status.error { color: #CC3333; }
  .file-status.idle { color: var(--muted); }

  .remove-btn { background: none; border: none; cursor: pointer; color: var(--muted); font-size: 18px; padding: 0 4px; line-height: 1; transition: color 0.15s; margin-left: 6px; }
  .remove-btn:hover { color: #CC3333; }

  @keyframes spin { to { transform: rotate(360deg); } }

  .mini-spinner { width: 11px; height: 11px; border: 1.5px solid currentColor; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; flex-shrink: 0; }

  .notice { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); padding: 10px 14px; background: var(--cream); border-radius: 10px; border: 1px solid var(--border); margin-top: 12px; }

  .chip-label { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }

  .chip { font-family: 'DM Sans', sans-serif; font-size: 13px; padding: 6px 14px; border-radius: 100px; border: 1px solid var(--border); background: transparent; color: var(--muted); cursor: pointer; transition: all 0.15s ease; }
  .chip:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
  .chip.active { border-color: var(--accent); background: var(--accent); color: white; }

  .btn-primary { width: 100%; margin-top: 16px; padding: 16px 32px; background: var(--ink); color: var(--cream); font-family: 'DM Sans', sans-serif; font-size: 15px; font-weight: 500; border: none; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s ease; }
  .btn-primary:hover:not(:disabled) { background: var(--accent); transform: translateY(-1px); box-shadow: 0 8px 24px rgba(212,98,42,0.3); }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

  .btn-secondary { width: 100%; margin-top: 12px; padding: 13px; background: transparent; color: var(--muted); font-family: 'DM Sans', sans-serif; font-size: 14px; border: 1px solid var(--border); border-radius: 12px; cursor: pointer; transition: all 0.15s; }
  .btn-secondary:hover { border-color: var(--ink); color: var(--ink); }

  .loading-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 40px 32px; text-align: center; }
  .loading-steps { display: flex; flex-direction: column; gap: 12px; margin-top: 24px; }

  .loading-step { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; font-size: 14px; color: var(--muted); background: var(--cream); transition: all 0.3s ease; }
  .loading-step.active { background: var(--accent-light); color: var(--accent); font-weight: 500; }
  .loading-step.done { color: var(--success); }

  .step-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; flex-shrink: 0; }
  .loading-step.active .step-dot { animation: pulse 1s ease-in-out infinite; }

  .big-spinner { width: 32px; height: 32px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 8px; }

  .result-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; animation: fadeUp 0.4s ease; }

  @keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

  .result-image-wrap { width: 100%; aspect-ratio: 1; background: var(--ink); overflow: hidden; }
  .result-image-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .result-image-placeholder { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--muted); font-size: 13px; gap: 8px; }

  .result-body { padding: 28px 32px 32px; }
  .result-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }

  .result-tag { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--success); background: #E8F5EE; padding: 4px 10px; border-radius: 100px; }

  .copy-btn { font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--muted); background: none; border: 1px solid var(--border); border-radius: 8px; padding: 5px 12px; cursor: pointer; transition: all 0.15s; }
  .copy-btn:hover { border-color: var(--ink); color: var(--ink); }

  .result-headline { font-family: 'Instrument Serif', serif; font-size: 26px; font-weight: 400; line-height: 1.3; margin-bottom: 12px; }
  .result-caption { font-size: 15px; line-height: 1.7; color: #4A4540; font-weight: 300; margin-bottom: 24px; }

  .eval-section { border-top: 1px solid var(--border); padding-top: 20px; }
  .eval-label { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 14px; }
  .eval-scores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .score-item { text-align: center; padding: 14px 8px; background: var(--cream); border-radius: 10px; }
  .score-value { font-family: 'Instrument Serif', serif; font-size: 28px; font-weight: 400; color: var(--ink); line-height: 1; }
  .score-value span { font-size: 13px; color: var(--muted); }
  .score-name { font-size: 11px; color: var(--muted); margin-top: 4px; }
  .eval-notes { font-size: 13px; line-height: 1.6; color: var(--muted); font-style: italic; padding: 12px 16px; background: var(--cream); border-radius: 8px; border-left: 2px solid var(--accent); }

  .error-card { background: #FFF5F5; border: 1px solid #FFCCCC; border-radius: var(--radius); padding: 20px 24px; font-size: 14px; color: #CC3333; display: flex; gap: 10px; align-items: flex-start; animation: fadeUp 0.3s ease; }
`;

const TOPICS = ["Product launch", "Brand story", "Behind the scenes", "Customer love", "Seasonal", "Announcement"];
const LOADING_STEPS = ["Searching brand context", "Generating caption", "Creating image", "Evaluating quality"];

function getFileIcon(name) {
  const ext = name.split(".").pop().toLowerCase();
  if (ext === "pdf") return "📄";
  if (["doc", "docx"].includes(ext)) return "📝";
  if (["txt", "md"].includes(ext)) return "🗒️";
  return "📎";
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

export default function App() {
  const [brandContext, setBrandContext] = useState("");
  const [topic, setTopic] = useState("");
  const [customTopic, setCustomTopic] = useState("");
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const activeTopic = topic || customTopic;
  const hasUploads = files.some(f => f.status === "done");
  const currentStep = result ? 3 : loading ? 2 : hasUploads || brandContext ? 1 : 0;

  async function uploadFile(fileObj, index) {
    setFiles(prev => prev.map((f, i) => i === index ? { ...f, status: "uploading" } : f));
    try {
      const formData = new FormData();
      formData.append("file", fileObj.file);

      const res = await fetch(`${API_BASE}/brands/${SESSION_BRAND_ID}/documents`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);

      const data = await res.json();
      setFiles(prev => prev.map((f, i) =>
        i === index ? { ...f, status: "done", docId: data.id || data.document_id } : f
      ));
    } catch (e) {
      console.error("Upload error:", e);
      setFiles(prev => prev.map((f, i) => i === index ? { ...f, status: "error" } : f));
    }
  }

  function addFiles(incoming) {
    const newEntries = Array.from(incoming).map(file => ({ file, status: "idle", docId: null }));
    setFiles(prev => {
      const updated = [...prev, ...newEntries];
      newEntries.forEach((_, i) => {
        const idx = prev.length + i;
        setTimeout(() => uploadFile(updated[idx], idx), 50 * i);
      });
      return updated;
    });
  }

  const simulate = (step, delay) =>
    new Promise(r => setTimeout(() => { setLoadingStep(step); r(); }, delay));

  async function handleGenerate() {
    if (!brandContext.trim() || !activeTopic.trim()) return;
    setLoading(true); setError(null); setResult(null); setLoadingStep(0);

    try {
      await simulate(1, 600);
      await simulate(2, 1200);
      await simulate(3, 1800);

      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_id: SESSION_BRAND_ID,        // ✅ scopes RAG to this session's uploads
          brand_context: brandContext,        // ✅ fallback if no docs uploaded
          topic: activeTopic,
          document_ids: files
            .filter(f => f.status === "done" && f.docId)
            .map(f => f.docId),
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${res.status}`);
      }

      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false); setLoadingStep(0);
    }
  }

  function handleCopy() {
    if (!result) return;
    navigator.clipboard.writeText(`${result.headline}\n\n${result.caption}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleReset() {
    setResult(null); setError(null);
    setBrandContext(""); setTopic(""); setCustomTopic(""); setFiles([]);
  }

  let evaluation = null;
  if (result?.evaluation) {
    try {
      evaluation = JSON.parse(result.evaluation.replace(/```json|```/g, "").trim());
    } catch (_) {}
  }

  const uploadingCount = files.filter(f => f.status === "uploading").length;
  const canGenerate = brandContext.trim() && activeTopic.trim() && !loading;

  return (
    <>
      <style>{styles}</style>
      <div className="app">

        <div className="header">
          <div className="header-eyebrow">AI Brand Studio</div>
          <h1>Create posts that<br /><em>actually</em> sound like you.</h1>
          <p>Feed it your brand voice. Get scroll-stopping content in seconds.</p>
        </div>

        <div className="steps">
          {["Brand setup", "Post details", "Generate"].map((label, i) => (
            <div key={label} style={{ display: "flex", alignItems: "center", flex: i < 2 ? 1 : "unset" }}>
              <div className={`step-item ${currentStep === i ? "active" : ""} ${currentStep > i ? "done" : ""}`}>
                <div className="step-num">{currentStep > i ? "✓" : i + 1}</div>
                {label}
              </div>
              {i < 2 && <div className="step-line" />}
            </div>
          ))}
        </div>

        {!result && !loading && (
          <>
            <div className="card">
              <div className="card-label">Brand voice</div>
              <div className="input-row">
                <div className="input-icon">✦</div>
                <textarea
                  rows={3}
                  placeholder="Describe your brand — tone, values, audience, what makes you different..."
                  value={brandContext}
                  onChange={e => setBrandContext(e.target.value)}
                />
              </div>
            </div>

            <div className="card">
              <div className="card-label">
                Brand documents
                <span style={{ color: "var(--border)", fontWeight: 400, textTransform: "none", letterSpacing: 0, marginLeft: 6 }}>
                  — optional but recommended
                </span>
              </div>
              <div
                className={`upload-zone ${dragOver ? "drag-over" : ""}`}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
              >
                <input
                  type="file" multiple accept=".pdf,.doc,.docx,.txt,.md"
                  onChange={e => e.target.files?.length && addFiles(e.target.files)}
                />
                <span className="upload-icon">📂</span>
                <div className="upload-title">Drop brand documents here</div>
                <div className="upload-sub"><span>Browse files</span> · PDF, DOCX, TXT, MD</div>
              </div>

              {files.length > 0 && (
                <div className="file-list">
                  {files.map((f, i) => (
                    <div className="file-item" key={i}>
                      <div className="file-item-left">
                        <div className="file-item-icon">{getFileIcon(f.file.name)}</div>
                        <div>
                          <div className="file-item-name">{f.file.name}</div>
                          <div className="file-item-size">{formatBytes(f.file.size)}</div>
                        </div>
                      </div>
                      <div style={{ display: "flex", alignItems: "center" }}>
                        <div className={`file-status ${f.status}`}>
                          {f.status === "uploading" && <><span className="mini-spinner" /> Uploading</>}
                          {f.status === "done" && <>✓ Ready</>}
                          {f.status === "error" && <>✗ Failed</>}
                          {f.status === "idle" && <>Queued</>}
                        </div>
                        <button className="remove-btn" onClick={() => setFiles(prev => prev.filter((_, j) => j !== i))}>×</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {uploadingCount > 0 && (
                <div className="notice">
                  <span className="mini-spinner" style={{ color: "var(--accent)" }} />
                  Uploading {uploadingCount} document{uploadingCount > 1 ? "s" : ""}...
                </div>
              )}
            </div>

            <div className="card">
              <div className="chip-label">Post topic</div>
              <div className="chips">
                {TOPICS.map(t => (
                  <button key={t} className={`chip ${topic === t ? "active" : ""}`}
                    onClick={() => { setTopic(t); setCustomTopic(""); }}>
                    {t}
                  </button>
                ))}
              </div>
              <div className="divider" />
              <div className="input-row">
                <div className="input-icon" style={{ background: "var(--cream)" }}>✏️</div>
                <input type="text" placeholder="Or write your own topic..."
                  value={customTopic}
                  onChange={e => { setCustomTopic(e.target.value); setTopic(""); }} />
              </div>
            </div>

            <button className="btn-primary" onClick={handleGenerate} disabled={!canGenerate}>
              Generate post →
            </button>
          </>
        )}

        {loading && (
          <div className="loading-card">
            <div className="big-spinner" />
            <p style={{ fontSize: 14, color: "var(--muted)", marginBottom: 4 }}>Working on it...</p>
            <div className="loading-steps">
              {LOADING_STEPS.map((step, i) => (
                <div key={step} className={`loading-step ${loadingStep === i ? "active" : ""} ${loadingStep > i ? "done" : ""}`}>
                  <div className="step-dot" />
                  {loadingStep > i ? "✓ " : ""}{step}
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <>
            <div className="error-card"><span>⚠</span><span>{error}</span></div>
            <button className="btn-secondary" onClick={handleReset}>Try again</button>
          </>
        )}

        {result && (
          <>
            <div className="result-card">
              <div className="result-image-wrap">
                {result.post_id ? (
                  <img
                    src={`${API_BASE}/outputs/${result.post_id}/post.png`}
                    alt="Generated post"
                    onError={e => { e.target.style.display = "none"; }}
                  />
                ) : (
                  <div className="result-image-placeholder">
                    <span style={{ fontSize: 32 }}>🖼</span>
                    <span>Image not available</span>
                  </div>
                )}
              </div>
              <div className="result-body">
                <div className="result-meta">
                  <span className="result-tag">✓ Generated</span>
                  <button className="copy-btn" onClick={handleCopy}>{copied ? "Copied!" : "Copy text"}</button>
                </div>
                {result.headline && <div className="result-headline">{result.headline}</div>}
                {result.caption && <div className="result-caption">{result.caption}</div>}
                {evaluation && (
                  <div className="eval-section">
                    <div className="eval-label">Quality scores</div>
                    <div className="eval-scores">
                      {["tone", "accuracy", "engagement"].map(k => (
                        <div className="score-item" key={k}>
                          <div className="score-value">{evaluation[k]}<span>/10</span></div>
                          <div className="score-name">{k}</div>
                        </div>
                      ))}
                    </div>
                    {evaluation.notes && <div className="eval-notes">{evaluation.notes}</div>}
                  </div>
                )}
              </div>
            </div>
            <button className="btn-secondary" onClick={handleReset}>← Generate another post</button>
          </>
        )}

      </div>
    </>
  );
}