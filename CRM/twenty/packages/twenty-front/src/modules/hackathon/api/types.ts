export type RelationshipStage =
  | 'new_lead'
  | 'contacted'
  | 'engaged'
  | 'customer'
  | 'inactive';

export type ActionType =
  | 'post_liked'
  | 'comment_posted'
  | 'skill_endorsed'
  | 'connection_request_sent'
  | 'message_sent'
  | 'profile_viewed';

export type ActionStatus = 'pending' | 'completed' | 'failed';

export type Contact = {
  id: string;
  name: string;
  title?: string | null;
  company?: string | null;
  email?: string | null;
  linkedin_url?: string | null;
  phone?: string | null;
  tags: string[];
  source?: string | null;
  relationship_stage: RelationshipStage;
  notes?: string | null;
  campaign_id?: string | null;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  archived_at?: string | null;
  last_interaction_at?: string | null;
};

export type Action = {
  id: string;
  contact_id: string;
  action_type: ActionType;
  action_details?: Record<string, unknown> | null;
  status: ActionStatus;
  timestamp?: string | null;
  metadata?: Record<string, unknown> | null;
  scheduled_for?: string | null;
  completed_at?: string | null;
};

export type PaginatedContacts = {
  total: number;
  items: Contact[];
};

export type CrmOverview = {
  total_contacts: number;
  active_campaigns: number;
  relationship_stage_counts: Record<string, number>;
  tag_counts: Record<string, number>;
  daily_action_counts: Array<{ date: string; count: number }>;
  recent_actions: Action[];
};
