export const APP_NAME = 'AutoMate';

export const PAGE_IDS = {
  AGENT: 'agent',
  LOGS: 'logs',
  EVALUATION: 'evaluation',
} as const;

export type PageId = (typeof PAGE_IDS)[keyof typeof PAGE_IDS];

export const NAV_ITEMS: { id: PageId; label: string; description: string }[] = [
  {
    id: PAGE_IDS.AGENT,
    label: 'Agent',
    description: 'Run and test the in-vehicle AI agent',
  },
  {
    id: PAGE_IDS.LOGS,
    label: 'Logs',
    description: 'Browse execution history',
  },
  {
    id: PAGE_IDS.EVALUATION,
    label: 'Evaluation',
    description: 'View performance metrics and distributions',
  },
];

export const EXAMPLE_PHRASES = [
  '나 좀 추워',
  '집으로 안내해줘',
  '운전 중이니까 엄마한테 전화해줘',
  '졸려',
  '조용한 노래 틀어줘',
  '창문 닫아줘',
  '비 오니까 와이퍼 자동으로 해줘',
  '배터리 상태 확인해줘',
  '운전 중인데 화면 설정 좀 복잡하게 바꿔줘',
] as const;

export const INTENT_LABELS: Record<string, string> = {
  CONTROL_CLIMATE: 'Climate Control',
  SET_NAVIGATION: 'Navigation',
  PLAY_MEDIA: 'Media',
  MAKE_CALL: 'Call',
  READ_SCHEDULE: 'Schedule',
  CHANGE_VEHICLE_SETTING: 'Vehicle Setting',
  CHECK_VEHICLE_STATUS: 'Vehicle Status',
  FIND_NEARBY_PLACE: 'Nearby Place',
  UNKNOWN: 'Unknown',
};
