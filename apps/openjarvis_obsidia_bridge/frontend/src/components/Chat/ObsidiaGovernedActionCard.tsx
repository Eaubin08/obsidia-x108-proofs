import {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Fingerprint,
  Loader2,
  LockKeyhole,
  ShieldAlert,
  XCircle,
} from 'lucide-react';

import {
  authorizeObsidiaGovernedCandidate,
  ensureObsidiaGovernedSession,
  fetchObsidiaGovernedStatus,
  prepareObsidiaGovernedCandidate,
} from '../../lib/api';

import type {
  ObsidiaGovernedResponse,
} from '../../lib/api';


function shortHash(value?: string | null): string {
  if (!value) return '-';
  if (value.length <= 24) return value;
  return `${value.slice(0, 14)}?${value.slice(-8)}`;
}


export function ObsidiaGovernedActionCard() {
  const [state, setState] =
    useState<ObsidiaGovernedResponse | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [busy, setBusy] =
    useState(false);

  const [candidatePath, setCandidatePath] =
    useState('');

  const [expanded, setExpanded] =
    useState(false);

  const [dismissedMission, setDismissedMission] =
    useState<string | null>(null);

  const refresh = useCallback(
    async () => {
      try {
        const result =
          await fetchObsidiaGovernedStatus();

        setState(result);
        setError(null);

        const mission =
          result.pending_governed_mission
            ?.relay_mission_id;

        if (
          mission
          && dismissedMission
          && mission !== dismissedMission
        ) {
          setDismissedMission(null);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : String(err),
        );
      }
    },
    [dismissedMission],
  );

  useEffect(() => {
    let alive = true;

    ensureObsidiaGovernedSession()
      .then(result => {
        if (!alive) return;
        setState(result);
        setError(null);
      })
      .catch(err => {
        if (!alive) return;
        setError(
          err instanceof Error
            ? err.message
            : String(err),
        );
      });

    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    const timer = window.setInterval(
      () => {
        void refresh();
      },
      2500,
    );

    return () => {
      window.clearInterval(timer);
    };
  }, [refresh]);

  const pending =
    state?.pending_governed_mission
      ?? null;

  const missionId =
    pending?.relay_mission_id
    ?? state?.relay_mission_id
    ?? null;

  const hidden =
    Boolean(
      missionId
      && missionId === dismissedMission,
    );

  const eah =
    pending?.execution_authority_hash
    ?? state?.execution_authority_hash
    ?? null;

  const exactEah =
    Boolean(
      eah
      && /^[0-9a-fA-F]{64}$/.test(eah),
    );

  const awaitingHuman =
    Boolean(
      pending
      && exactEah
      && !state?.real_execution
      && !hidden,
    );

  const handlePrepare =
    async () => {
      const path =
        candidatePath.trim();

      if (!path || busy) {
        return;
      }

      setBusy(true);

      try {
        const result =
          await prepareObsidiaGovernedCandidate(
            path,
          );

        setState(result);
        setError(null);
        setDismissedMission(null);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : String(err),
        );
      } finally {
        setBusy(false);
      }
    };

  const handleAuthorize =
    async () => {
      if (
        !eah
        || !exactEah
        || busy
      ) {
        return;
      }

      setBusy(true);

      try {
        const result =
          await authorizeObsidiaGovernedCandidate(
            eah,
          );

        setState(result);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : String(err),
        );
      } finally {
        setBusy(false);
      }
    };

  return (
    <div
      className="mx-4 mb-3 rounded-lg overflow-hidden"
      style={{
        border:
          '1px solid var(--color-border)',
        background:
          'var(--color-bg-secondary)',
      }}
    >
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left cursor-pointer"
        style={{
          background: 'transparent',
        }}
      >
        {expanded
          ? <ChevronDown size={12} />
          : <ChevronRight size={12} />}

        <LockKeyhole
          size={13}
          style={{
            color: 'var(--color-accent)',
          }}
        />

        <span
          className="text-[11px] font-semibold"
          style={{
            color: 'var(--color-text)',
          }}
        >
          Obsidia governed action
        </span>

        <span
          className="text-[9px] font-mono px-1.5 py-0.5 rounded"
          style={{
            color: 'var(--color-accent)',
            background:
              'var(--color-accent-subtle)',
          }}
        >
          KX108_ONLY
        </span>

        <div className="flex-1" />

        {busy && (
          <Loader2
            size={12}
            className="animate-spin"
            style={{
              color:
                'var(--color-text-secondary)',
            }}
          />
        )}

        {awaitingHuman && (
          <span
            className="text-[9px] font-semibold px-1.5 py-0.5 rounded"
            style={{
              color:
                'var(--color-warning)',
              background:
                'color-mix(in srgb, var(--color-warning) 12%, transparent)',
            }}
          >
            HOLD
          </span>
        )}

        {state?.real_execution && (
          <CheckCircle2
            size={13}
            style={{
              color:
                'var(--color-success)',
            }}
          />
        )}
      </button>

      {expanded && (
        <div
          className="px-3 pb-3 pt-1"
          style={{
            borderTop:
              '1px solid var(--color-border)',
          }}
        >
          <div
            className="text-[10px] mb-3"
            style={{
              color:
                'var(--color-text-secondary)',
            }}
          >
            OpenJarvis pr?sente l'action.
            Obsidia gouverne l'autorisation.
            Cette interface n'a aucune autorit? propre.
          </div>

          {error && (
            <div
              className="mb-3 rounded-md px-2.5 py-2 text-[10px]"
              style={{
                color:
                  'var(--color-error)',
                background:
                  'color-mix(in srgb, var(--color-error) 9%, transparent)',
                border:
                  '1px solid color-mix(in srgb, var(--color-error) 20%, transparent)',
              }}
            >
              Obsidia unavailable: {error}
            </div>
          )}

          {!pending && !state?.real_execution && (
            <div className="flex gap-2">
              <input
                value={candidatePath}
                onChange={event =>
                  setCandidatePath(
                    event.target.value,
                  )
                }
                onKeyDown={event => {
                  if (
                    event.key === 'Enter'
                  ) {
                    void handlePrepare();
                  }
                }}
                placeholder="Candidate .patch path"
                className="flex-1 rounded-md px-2.5 py-1.5 text-[11px] font-mono outline-none"
                style={{
                  background:
                    'var(--color-bg-tertiary)',
                  color:
                    'var(--color-text)',
                  border:
                    '1px solid var(--color-border)',
                }}
              />

              <button
                onClick={() =>
                  void handlePrepare()
                }
                disabled={
                  busy
                  || !candidatePath.trim()
                }
                className="px-3 py-1.5 rounded-md text-[10px] font-semibold cursor-pointer disabled:opacity-40"
                style={{
                  color:
                    'var(--color-accent)',
                  background:
                    'var(--color-accent-subtle)',
                  border:
                    '1px solid var(--color-border)',
                }}
              >
                PREPARE
              </button>
            </div>
          )}

          {pending && !hidden && (
            <div>
              <div
                className="rounded-md p-2.5 space-y-1 text-[10px] font-mono"
                style={{
                  background:
                    'var(--color-bg-tertiary)',
                  color:
                    'var(--color-text-secondary)',
                }}
              >
                <div>
                  target = {pending.target ?? '-'}
                </div>

                <div>
                  mission = {shortHash(missionId)}
                </div>

                <div>
                  candidate = {shortHash(
                    pending.candidate_patch_sha256,
                  )}
                </div>

                <div
                  style={{
                    color:
                      'var(--color-text)',
                  }}
                >
                  EAH = {eah ?? '-'}
                </div>
              </div>

              {awaitingHuman && (
                <div
                  className="mt-3 rounded-md p-2.5"
                  style={{
                    background:
                      'color-mix(in srgb, var(--color-warning) 8%, transparent)',
                    border:
                      '1px solid color-mix(in srgb, var(--color-warning) 20%, transparent)',
                  }}
                >
                  <div className="flex gap-2">
                    <Fingerprint
                      size={14}
                      style={{
                        color:
                          'var(--color-warning)',
                        flexShrink: 0,
                      }}
                    />

                    <div className="flex-1">
                      <div
                        className="text-[10px] font-semibold"
                        style={{
                          color:
                            'var(--color-warning)',
                        }}
                      >
                        Exact human EAH authorization required
                      </div>

                      <div
                        className="mt-1 text-[9px]"
                        style={{
                          color:
                            'var(--color-text-secondary)',
                        }}
                      >
                        No action has executed yet.
                        Natural-language approval is not accepted.
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => {
                        if (missionId) {
                          setDismissedMission(
                            missionId,
                          );
                        }
                      }}
                      className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-[10px] font-semibold cursor-pointer"
                      style={{
                        color:
                          'var(--color-error)',
                        background:
                          'color-mix(in srgb, var(--color-error) 8%, transparent)',
                        border:
                          '1px solid color-mix(in srgb, var(--color-error) 20%, transparent)',
                      }}
                      title="Does not execute. Mission remains HOLD in Obsidia."
                    >
                      <XCircle size={11} />
                      Ne pas autoriser
                    </button>

                    <button
                      onClick={() =>
                        void handleAuthorize()
                      }
                      disabled={
                        busy
                        || !exactEah
                      }
                      className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-[10px] font-semibold cursor-pointer disabled:opacity-40"
                      style={{
                        color:
                          'var(--color-success)',
                        background:
                          'color-mix(in srgb, var(--color-success) 10%, transparent)',
                        border:
                          '1px solid color-mix(in srgb, var(--color-success) 24%, transparent)',
                      }}
                    >
                      <LockKeyhole size={11} />
                      Autoriser cette EAH
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {hidden && (
            <div
              className="text-[10px] rounded-md px-2.5 py-2"
              style={{
                color:
                  'var(--color-text-secondary)',
                background:
                  'var(--color-bg-tertiary)',
              }}
            >
              Non autoris?e dans cette interface.
              La mission reste HOLD c?t? Obsidia et aucune action n'est ex?cut?e.
            </div>
          )}

          {state?.real_execution && (
            <div
              className="rounded-md px-2.5 py-2"
              style={{
                color:
                  'var(--color-success)',
                background:
                  'color-mix(in srgb, var(--color-success) 8%, transparent)',
                border:
                  '1px solid color-mix(in srgb, var(--color-success) 20%, transparent)',
              }}
            >
              <div className="flex items-center gap-1.5 text-[10px] font-semibold">
                <CheckCircle2 size={12} />
                {state.mission_state
                  ?? state.status}
              </div>
            </div>
          )}

          {state?.surface_text && (
            <pre
              className="mt-3 rounded-md p-2.5 overflow-auto text-[9px] leading-relaxed"
              style={{
                maxHeight: 180,
                background:
                  'var(--color-bg-tertiary)',
                color:
                  'var(--color-text-secondary)',
                whiteSpace:
                  'pre-wrap',
                wordBreak:
                  'break-word',
              }}
            >
              {state.surface_text}
            </pre>
          )}

          <div
            className="mt-2 flex gap-3 text-[8px] font-mono"
            style={{
              color:
                'var(--color-text-tertiary)',
            }}
          >
            <span>UI_AUTHORITY=NONE</span>
            <span>AUTO_EXECUTE=false</span>
            <span>NATIVE_APPROVAL_AUTHORITY=false</span>
          </div>
        </div>
      )}
    </div>
  );
}
