import {
  ApprovalEvent,
  CompletedAt,
  EvalError,
  EvalId,
  EvalLog,
  EvalMetric,
  EvalPlan,
  EvalResults,
  EvalSample,
  EvalSpec,
  EvalStats,
  InfoEvent,
  Input,
  LoggerEvent,
  Model,
  ModelEvent,
  RunId,
  SampleInitEvent,
  SampleLimitEvent,
  SandboxEvent,
  ScoreEvent,
  Scores1,
  StartedAt,
  StateEvent,
  Status,
  StepEvent,
  StoreEvent,
  SubtaskEvent,
  Target,
  Task,
  TaskId,
  TaskVersion,
  ToolEvent,
  Version,
} from "../../@types/log";

export interface EvalSummary {
  version?: Version;
  status?: Status;
  eval: EvalSpec;
  plan?: EvalPlan;
  results?: EvalResults | null;
  stats?: EvalStats;
  error?: EvalError | null;
  sampleSummaries: SampleSummary[];
}

export interface PendingSampleResponse {
  pendingSamples?: PendingSamples;
  status: "NotModified" | "NotFound" | "OK";
}

export interface SampleDataResponse {
  sampleData?: SampleData;
  status: "NotModified" | "NotFound" | "OK";
}

export interface RunningMetric {
  scorer: string;
  name: string;
  value?: number | null;
  reducer?: string;
}

export interface PendingSamples {
  metrics?: RunningMetric[];
  samples: SampleSummary[];
  refresh: number;
  etag?: string;
}

export interface SampleData {
  events: EventData[];
  attachments: AttachmentData[];
}

export interface EventData {
  id: number;
  event_id: string;
  sample_id: string;
  epoch: number;
  event:
    | SampleInitEvent
    | SampleLimitEvent
    | SandboxEvent
    | StateEvent
    | StoreEvent
    | ModelEvent
    | ToolEvent
    | ApprovalEvent
    | InputEvent
    | ScoreEvent
    | ErrorEvent
    | LoggerEvent
    | InfoEvent
    | StepEvent
    | SubtaskEvent;
}

export interface AttachmentData {
  id: number;
  sample_id: string;
  epoch: number;
  hash: string;
  content: string;
}

export interface EvalLogHeader {
  version?: Version;
  status?: Status;
  eval: EvalSpec;
  plan?: EvalPlan;
  results?: EvalResults;
  stats?: EvalStats;
  error?: EvalError;
}

export interface SampleSummary {
  uuid?: string;
  id: number | string;
  epoch: number;
  input: Input;
  target: Target;
  scores: Scores1;
  error?: string;
  limit?: string;
  metadata?: Record<string, any>;
  completed?: boolean;
  retries?: number;
}

export interface BasicSampleData {
  id: number | string;
  epoch: number;
  target: Target;
  scores: Scores1;
}

export interface Capabilities {
  downloadFiles: boolean;
  webWorkers: boolean;
  streamSamples: boolean;
  streamSampleData: boolean;
  nativeFind: boolean;
}

export interface LogViewAPI {
  client_events: () => Promise<any[]>;
  eval_logs: () => Promise<LogFiles | undefined>;
  eval_log: (
    log_file: string,
    headerOnly?: number,
    capabilities?: Capabilities,
  ) => Promise<LogContents>;
  eval_log_size: (log_file: string) => Promise<number>;
  eval_log_bytes: (
    log_file: string,
    start: number,
    end: number,
  ) => Promise<Uint8Array>;
  eval_log_overview?: (log_file: string) => Promise<LogOverview>;
  eval_log_overviews: (log_files: string[]) => Promise<LogOverview[]>;
  log_message: (log_file: string, message: string) => Promise<void>;
  download_file: (
    filename: string,
    filecontents: string | Blob | ArrayBuffer | ArrayBufferView,
  ) => Promise<void>;
  open_log_file: (logFile: string, log_dir: string) => Promise<void>;
  eval_pending_samples?: (
    log_file: string,
    etag?: string,
  ) => Promise<PendingSampleResponse>;
  eval_log_sample_data?: (
    log_file: string,
    id: string | number,
    epoch: number,
    last_event?: number,
    last_attachment?: number,
  ) => Promise<SampleDataResponse | undefined>;
}

export interface ClientAPI {
  client_events: () => Promise<string[]>;
  get_log_paths: () => Promise<LogFiles>;
  get_log_overviews: (log_files: string[]) => Promise<LogOverview[]>;
  get_log_summary: (log_file: string) => Promise<EvalSummary>;
  get_log_sample: (
    log_file: string,
    id: string | number,
    epoch: number,
  ) => Promise<EvalSample | undefined>;
  log_message?: (log_file: string, message: string) => Promise<void>;
  download_file: (
    file_name: string,
    file_contents: string | Blob | ArrayBuffer | ArrayBufferView,
  ) => Promise<void>;
  open_log_file: (log_file: string, log_dir: string) => Promise<void>;

  get_log_pending_samples?: (
    log_file: string,
    etag?: string,
  ) => Promise<PendingSampleResponse>;
  get_log_sample_data?: (
    log_file: string,
    id: string | number,
    epoch: number,
    last_event?: number,
    last_attachment?: number,
  ) => Promise<SampleDataResponse | undefined>;
}

export interface ClientStorage {
  getItem: (name: string) => unknown;
  setItem: (name: string, value: unknown) => void;
  removeItem: (name: string) => void;
}

export interface FetchResponse {
  raw: string;
  parsed: Record<string, any>;
}

export interface EvalHeader {
  version?: Version;
  status?: Status;
  eval: EvalSpec;
  plan?: EvalPlan;
  results?: EvalResults | null;
  stats?: EvalStats;
  error?: EvalError | null;
}

export interface LogOverview {
  eval_id: EvalId;
  run_id: RunId;

  task: Task;
  task_id: TaskId;
  task_version: TaskVersion;

  version?: Version;
  status?: Status;
  error?: EvalError | null;

  model: Model;

  started_at?: StartedAt;
  completed_at?: CompletedAt;

  primary_metric?: EvalMetric;
}

export interface LogFiles {
  files: LogFile[];
  log_dir?: string;
}

export interface LogFile {
  name: string;
  task?: string;
  task_id?: string;
}

export interface LogContents {
  raw: string;
  parsed: EvalLog;
}

export interface LogFilesFetchResponse {
  raw: string;
  parsed: Record<string, LogOverview>;
}

export interface UpdateStateMessage {
  data: {
    type: "updateState";
    url: string;
    sample_id?: string;
    sample_epoch?: string;
  };
}

export interface BackgroundUpdateMessage {
  data: {
    type: "backgroundUpdate";
    url: string;
    log_dir: string;
  };
}
export type HostMessage = UpdateStateMessage | BackgroundUpdateMessage;
