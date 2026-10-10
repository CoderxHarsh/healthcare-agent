import { queryOptions } from '@tanstack/react-query'
import { api } from './client'

export const profileQuery = (userId: number) =>
  queryOptions({
    queryKey: ['profile', userId],
    queryFn: () => api.getProfile(userId),
  })

export const healthLogsQuery = (userId: number, days: number, metricType?: string) =>
  queryOptions({
    queryKey: ['health-logs', userId, days, metricType ?? null],
    queryFn: () => api.getHealthLogs(userId, { days, metricType }),
  })

export const healthSummaryQuery = (userId: number, days: number) =>
  queryOptions({
    queryKey: ['health-logs', userId, 'summary', days],
    queryFn: () => api.getHealthSummary(userId, days),
  })

export const vitalsSummaryQuery = (userId: number) =>
  queryOptions({
    queryKey: ['vitals-summary', userId],
    queryFn: () => api.getVitalsSummary(userId),
    // Each call runs an LLM request on the backend, so don't refetch on every visit.
    staleTime: 5 * 60_000,
    retry: false,
  })

export const medicationsQuery = (userId: number) =>
  queryOptions({
    queryKey: ['medications', userId],
    queryFn: () => api.getMedications(userId),
  })

export const adherenceQuery = (userId: number, days: number) =>
  queryOptions({
    queryKey: ['medications', userId, 'adherence', days],
    queryFn: () => api.getAdherence(userId, days),
  })
