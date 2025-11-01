import { useCallback, useEffect, useMemo, useState } from 'react';

import { CRM_API_BASE_URL } from './constants';
import type {
  Contact,
  CrmOverview,
  PaginatedContacts,
  RelationshipStage,
} from './types';

type UseHackathonCrmDashboardDataArgs = {
  search?: string;
  relationshipStage?: RelationshipStage | 'all';
  tags?: string[];
};

type HackathonCrmDashboardState = {
  contacts: Contact[];
  overview: CrmOverview | null;
  isLoading: boolean;
  error?: string;
  refresh: () => void;
};

const buildQueryString = (params: Record<string, string | string[] | undefined>) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (!value || (Array.isArray(value) && value.length === 0)) {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => query.append(key, item));
    } else {
      query.set(key, value);
    }
  });
  return query.toString();
};

export const useHackathonCrmDashboardData = ({
  search,
  relationshipStage,
  tags,
}: UseHackathonCrmDashboardDataArgs): HackathonCrmDashboardState => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [overview, setOverview] = useState<CrmOverview | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [refreshIndex, setRefreshIndex] = useState(0);

  const refresh = useCallback(() => {
    setRefreshIndex((value) => value + 1);
  }, []);

  const relationshipParam = relationshipStage && relationshipStage !== 'all' ? relationshipStage : undefined;

  useEffect(() => {
    const controller = new AbortController();
    const run = async () => {
      setIsLoading(true);
      setError(undefined);
      try {
        const query = buildQueryString({
          search,
          relationship_stage: relationshipParam,
          tags,
        });
        const contactsResponse = await fetch(
          `${CRM_API_BASE_URL}/contacts${query ? `?${query}` : ''}`,
          { signal: controller.signal },
        );
        const overviewResponse = await fetch(`${CRM_API_BASE_URL}/stats/overview`, {
          signal: controller.signal,
        });

        if (!contactsResponse.ok) {
          throw new Error(`Failed to load contacts (${contactsResponse.status})`);
        }
        if (!overviewResponse.ok) {
          throw new Error(`Failed to load CRM overview (${overviewResponse.status})`);
        }

        const contactsPayload = (await contactsResponse.json()) as PaginatedContacts;
        const overviewPayload = (await overviewResponse.json()) as CrmOverview;

        setContacts(contactsPayload.items);
        setOverview(overviewPayload);
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          return;
        }
        const { message } = err as Error;
        setError(
          message ? `Unable to load CRM data (${message}).` : 'Unable to load CRM data.',
        );
      } finally {
        setIsLoading(false);
      }
    };

    void run();
    return () => controller.abort();
  }, [search, relationshipParam, tags, refreshIndex]);

  const normalizedContacts = useMemo(() => {
    if (!search) {
      return contacts;
    }
    const lower = search.toLowerCase();
    return contacts.filter((contact) =>
      [contact.name, contact.company, contact.title]
        .filter(Boolean)
        .some((value) => value?.toLowerCase().includes(lower)),
    );
  }, [contacts, search]);

  return {
    contacts: normalizedContacts,
    overview,
    isLoading,
    error,
    refresh,
  };
};
