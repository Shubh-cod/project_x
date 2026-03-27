export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role?: string;
  is_active?: boolean;
  avatar_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Contact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  address?: string;
  source?: string;
  notes?: string;
  assigned_to?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  title: string;
  contact_id: string;
  source: string;
  status: "new" | "contacted" | "qualified" | "lost";
  priority: "low" | "medium" | "high";
  assigned_to?: string;
  estimated_value?: number;
  notes?: string;
  status_changed_at?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

export interface Deal {
  id: string;
  title: string;
  contact_id: string;
  lead_id?: string;
  stage: "prospect" | "proposal" | "negotiation" | "won" | "lost";
  value: number;
  currency: string;
  close_date?: string;
  probability?: number;
  assigned_to?: string;
  notes?: string;
  won_reason?: string;
  lost_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  due_date?: string;
  priority: string;
  status: string;
  linked_to_type?: string;
  linked_to_id?: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  content: string;
  entity_type: string;
  entity_id: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface EmailLog {
  id: string;
  subject: string;
  body_preview?: string;
  sent_at: string;
  contact_id: string;
  sent_by?: string;
  created_at: string;
  updated_at: string;
}

export interface Activity {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  user_id?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  summary: {
    total_contacts: number;
    open_leads: number;
    deals_won_this_month: number;
    tasks_due_today: number;
  };
  pipeline_by_stage: {
    stage: string;
    count: number;
    total_value: number;
  }[];
  agent_performance: {
    user_id: string;
    full_name: string;
    deals_won: number;
    leads_contacted: number;
  }[];
}

export interface SearchResultItem {
  type: "contact" | "lead" | "deal";
  id: string;
  title: string;
  subtitle?: string;
}

export interface SearchResults {
  contacts: SearchResultItem[];
  leads: SearchResultItem[];
  deals: SearchResultItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
