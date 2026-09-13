import { useState } from "react";

const STAGES = [
  {
    id: "search",
    icon: "⌕",
    title: "Search",
    description: "Find live opportunities",
  },
  {
    id: "extract",
    icon: "◈",
    title: "Read",
    description: "Understand requirements",
  },
  {
    id: "eligibility",
    icon: "✓",
    title: "Check",
    description: "Verify your eligibility",
  },
  {
    id: "score",
    icon: "✦",
    title: "Score",
    description: "Rank your best fits",
  },
  {
    id: "act",
    icon: "→",
    title: "Act",
    description: "Prepare your application",
  },
];

const STAGE_LABELS = {
  search: "Search live opportunities",
  extract: "Read & extract requirements",
  eligibility: "Check your eligibility",
  score: "Score & rank opportunities",
  act: "Prepare application",
  done: "Complete",
};

const DEFAULT_PROFILE = {
  name: "",
  education_level: "",
  grad_year: "",
  skills: "",
  location: "",
  visa_status: "",
  interests: "",
};

const QUICK_SEARCHES = [
  "AI internships in India",
  "Machine learning internships",
  "AI hackathons I can join",
  "Scholarships for AI students",
];

export default function Home() {
  const [query, setQuery] = useState(
    "Find me 5 AI internships I can apply to this week"
  );

  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [log, setLog] = useState([]);
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState(null);

  function updateProfile(key, value) {
    setProfile((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function getStageState(stageId) {
    const entry = [...log]
      .reverse()
      .find((item) => item.stage === stageId);

    if (!entry) {
      return "";
    }

    if (entry.status === "running") {
      return "active";
    }

    if (entry.status === "done") {
      return "complete";
    }

    return "";
  }

  async function startSearch() {
    if (!query.trim() || running) return;

    setLog([]);
    setResults(null);
    setRunning(true);

    try {
      const response = await fetch("/api/discover", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          profile,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Agent request failed with status ${response.status}`
        );
      }

      if (!response.body) {
        throw new Error("The agent returned no response stream.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, {
          stream: true,
        });

        const chunks = buffer.split("\n\n");

        buffer = chunks.pop() || "";

        for (const chunk of chunks) {
          if (!chunk.startsWith("data:")) continue;

          const payload = chunk
            .slice(5)
            .trim();

          if (!payload) continue;

          try {
            const update = JSON.parse(payload);

            setLog((previous) => [
              ...previous,
              update,
            ]);

            if (
              update.stage === "done" &&
              Array.isArray(update.data)
            ) {
              setResults(update.data);
            }
          } catch (parseError) {
            console.error(
              "Could not parse agent update:",
              parseError
            );
          }
        }
      }
    } catch (error) {
      console.error(error);

      setLog((previous) => [
        ...previous,
        {
          stage: "error",
          status: "error",
          message:
            error.message ||
            "Connection to the agent backend failed.",
        },
      ]);
    } finally {
      setRunning(false);
    }
  }

  function copyDraft(index, text) {
    if (!text) return;

    navigator.clipboard
      .writeText(text)
      .then(() => {
        setCopiedIdx(index);

        setTimeout(() => {
          setCopiedIdx(null);
        }, 1500);
      })
      .catch((error) => {
        console.error(
          "Could not copy draft:",
          error
        );
      });
  }

  function selectQuickSearch(search) {
    setQuery(search);
  }

  return (
    <div className="wrap">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="masthead">

        <div className="brand-row">
          <div className="brand-mark">✦</div>

          <div className="brand-name">
            OpportunityOS
          </div>
        </div>

        <h1>
          Find opportunities
          <br />
          <span className="gradient-text">
            worth applying to.
          </span>
        </h1>

        <p>
          Your AI opportunity agent searches the live web,
          reads requirements, checks your eligibility,
          ranks the best matches, and prepares you to act.
        </p>

      </header>


      {/* =====================================================
          SEARCH
      ====================================================== */}

      <section className="search-card">

        <div className="search-row">

          <input
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                startSearch();
              }
            }}
            placeholder="What opportunity are you looking for?"
            aria-label="Opportunity search"
          />

          <button
            className="primary"
            onClick={startSearch}
            disabled={running}
          >
            {running
              ? "Working..."
              : "Run agent →"}
          </button>

        </div>

      </section>


      {/* =====================================================
          QUICK SEARCHES
      ====================================================== */}

      <div className="quick-searches">

        {QUICK_SEARCHES.map((search) => (
          <button
            key={search}
            onClick={() =>
              selectQuickSearch(search)
            }
          >
            {search}
          </button>
        ))}

      </div>


      {/* =====================================================
          PROFILE
      ====================================================== */}

      <details className="profile-panel">

        <summary>
          Your profile · used for eligibility, scoring
          & personalized drafts
        </summary>

        <div className="profile-grid">

          <label>
            Name

            <input
              value={profile.name}
              onChange={(event) =>
                updateProfile(
                  "name",
                  event.target.value
                )
              }
            />
          </label>


          <label>
            Education level

            <input
              placeholder="e.g. undergraduate, B.Sc AI & ML"
              value={profile.education_level}
              onChange={(event) =>
                updateProfile(
                  "education_level",
                  event.target.value
                )
              }
            />
          </label>


          <label>
            Graduation year

            <input
              placeholder="e.g. 2027"
              value={profile.grad_year}
              onChange={(event) =>
                updateProfile(
                  "grad_year",
                  event.target.value
                )
              }
            />
          </label>


          <label>
            Location

            <input
              placeholder="city / country / remote"
              value={profile.location}
              onChange={(event) =>
                updateProfile(
                  "location",
                  event.target.value
                )
              }
            />
          </label>


          <label>
            Work authorization

            <input
              placeholder="optional"
              value={profile.visa_status}
              onChange={(event) =>
                updateProfile(
                  "visa_status",
                  event.target.value
                )
              }
            />
          </label>


          <label>
            Skills

            <input
              placeholder="Python, ML, React..."
              value={profile.skills}
              onChange={(event) =>
                updateProfile(
                  "skills",
                  event.target.value
                )
              }
            />
          </label>


          <label
            style={{
              gridColumn: "1 / -1",
            }}
          >
            Interests / target roles

            <input
              placeholder="AI research, data science, internships..."
              value={profile.interests}
              onChange={(event) =>
                updateProfile(
                  "interests",
                  event.target.value
                )
              }
            />
          </label>

        </div>

      </details>


      {/* =====================================================
          AGENT PIPELINE
      ====================================================== */}

      <section className="agent-panel">

        <div className="agent-heading">

          <h2>
            How the agent works
          </h2>

          <span>
            Read · Reason · Act
          </span>

        </div>


        <div className="agent-pipeline">

          {STAGES.map((stage) => {

            const state =
              getStageState(stage.id);

            return (
              <div
                key={stage.id}
                className={`agent-step ${state}`}
              >

                <div className="agent-icon">
                  {state === "complete"
                    ? "✓"
                    : stage.icon}
                </div>

                <strong>
                  {stage.title}
                </strong>

                <small>
                  {stage.description}
                </small>

              </div>
            );
          })}

        </div>

      </section>


      {/* =====================================================
          LIVE LOG
      ====================================================== */}

      {log.length > 0 && (
        <section className="log">

          {log.map((entry, index) => (

            <div
              key={index}
              className={`log-step ${entry.status}`}
            >

              <strong>
                {STAGE_LABELS[entry.stage] ||
                  entry.stage}
              </strong>

              <span>
                {entry.message}
              </span>

            </div>

          ))}

        </section>
      )}


      {/* =====================================================
          RESULTS
      ====================================================== */}

      {results &&
        results.length > 0 && (
          <section>

            <div className="results-header">

              <div>

                <h2>
                  Best matches for you
                </h2>

                <p>
                  Ranked by eligibility,
                  relevance and opportunity value.
                </p>

              </div>

              <span className="results-count">
                {results.length}{" "}
                {results.length === 1
                  ? "opportunity"
                  : "opportunities"}
              </span>

            </div>


            <div className="results">

              {results.map((result, index) => {

                const eligibility =
                  result.eligibility || {};

                const eligible =
                  eligibility.eligible;

                const badgeClass =
                  eligible === true
                    ? "eligible"
                    : eligible === false
                    ? "ineligible"
                    : "unclear";

                const badgeText =
                  eligible === true
                    ? "✓ Eligible"
                    : eligible === false
                    ? "Not eligible"
                    : "Eligibility unclear";

                return (
                  <article
                    className="card"
                    key={
                      result.url ||
                      result.apply_url ||
                      index
                    }
                  >

                    {/* -----------------------------------------
                        CARD HEADER
                    ------------------------------------------ */}

                    <div className="card-head">

                      <div className="card-title-area">

                        <h3>
                          {result.title ||
                            "Untitled opportunity"}
                        </h3>

                        <div className="organization">
                          {result.organization ||
                            "Organization not specified"}
                        </div>

                      </div>


                      <div className="score-box">

                        <span className="score">
                          {result.score ?? 0}
                        </span>

                        <span className="score-label">
                          fit score
                        </span>

                      </div>

                    </div>


                    {/* -----------------------------------------
                        META
                    ------------------------------------------ */}

                    <div className="meta-row">

                      {result.type && (
                        <span className="meta-pill">
                          ◇ {result.type}
                        </span>
                      )}

                      {result.location && (
                        <span className="meta-pill">
                          ◉ {result.location}
                        </span>
                      )}

                      {result.deadline && (
                        <span className="meta-pill">
                          ⏱ Deadline:{" "}
                          {result.deadline}
                        </span>
                      )}

                      {result.stipend_or_prize &&
                        result.stipend_or_prize !==
                          "unknown" && (
                          <span className="meta-pill">
                            ✦{" "}
                            {result.stipend_or_prize}
                          </span>
                        )}

                    </div>


                    {/* -----------------------------------------
                        ELIGIBILITY
                    ------------------------------------------ */}

                    <span
                      className={`badge ${badgeClass}`}
                    >
                      {badgeText}
                    </span>


                    {/* -----------------------------------------
                        SUMMARY
                    ------------------------------------------ */}

                    {result.summary && (
                      <p className="summary-text">
                        {result.summary}
                      </p>
                    )}


                    {/* -----------------------------------------
                        SCORE RATIONALE
                    ------------------------------------------ */}

                    {result.score_rationale && (
                      <div className="match-reason">

                        <strong>
                          Why this matches
                        </strong>

                        <p>
                          {result.score_rationale}
                        </p>

                      </div>
                    )}


                    {/* -----------------------------------------
                        ELIGIBILITY REASONS
                    ------------------------------------------ */}

                    {eligibility.reasons &&
                      eligibility.reasons.length >
                        0 && (
                        <details className="section">

                          <summary>
                            Why you're eligible
                          </summary>

                          <ul className="checklist">

                            {eligibility.reasons.map(
                              (reason, reasonIndex) => (
                                <li
                                  key={reasonIndex}
                                >
                                  {reason}
                                </li>
                              )
                            )}

                          </ul>

                        </details>
                      )}


                    {/* -----------------------------------------
                        CHECKLIST
                    ------------------------------------------ */}

                    {result.checklist &&
                      result.checklist.length >
                        0 && (
                        <details className="section">

                          <summary>
                            Application checklist
                          </summary>

                          <ul className="checklist">

                            {result.checklist.map(
                              (step, stepIndex) => (
                                <li
                                  key={stepIndex}
                                >
                                  {step}
                                </li>
                              )
                            )}

                          </ul>

                        </details>
                      )}


                    {/* -----------------------------------------
                        DRAFT
                    ------------------------------------------ */}

                    {result.draft_email && (
                      <details className="section">

                        <summary>
                          Tailored application draft
                        </summary>

                        <div className="draft-box">
                          {result.draft_email}
                        </div>

                        <div className="card-actions">

                          <button
                            onClick={() =>
                              copyDraft(
                                index,
                                result.draft_email
                              )
                            }
                          >
                            {copiedIdx === index
                              ? "✓ Copied"
                              : "Copy draft"}
                          </button>

                        </div>

                      </details>
                    )}


                    {/* -----------------------------------------
                        ACTIONS
                    ------------------------------------------ */}

                    <div className="card-actions">

                      {result.apply_url && (
                        <a
                          className="apply"
                          href={result.apply_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open application →
                        </a>
                      )}

                    </div>

                  </article>
                );
              })}

            </div>

          </section>
        )}


      {/* =====================================================
          EMPTY STATE
      ====================================================== */}

      {results &&
        results.length === 0 && (
          <div className="empty-state">

            <strong>
              No actionable opportunities found.
            </strong>

            <br />

            Try a broader search or a different
            opportunity type.

          </div>
        )}

    </div>
  );
}