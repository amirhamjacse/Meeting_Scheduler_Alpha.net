"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { meetingsApi } from "@/lib/api";
import {
  formatDateTime,
  getMeetingStatusColor,
  downloadBlob,
  extractErrorMessage,
} from "@/lib/utils";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useToast } from "@/components/Toast";
import {
  PlusCircle,
  Search,
  Download,
  CalendarDays,
  Clock,
  MapPin,
  Users,
  Filter,
} from "lucide-react";

const STATUS_OPTIONS = [
  { value: "", label: "All Status" },
  { value: "scheduled", label: "Scheduled" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
];

export default function MeetingsPage() {
  const toast = useToast();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [exportingId, setExportingId] = useState(null);

  const fetchMeetings = useCallback(async () => {
    setLoading(true);
    try {
      const params = { ordering: "start_time" };
      if (search) params.search = search;
      if (status) params.status = status;
      if (fromDate) params.from_date = fromDate;
      if (toDate) params.to_date = toDate;
      const { data } = await meetingsApi.list(params);
      setMeetings(data.results ?? data);
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setLoading(false);
    }
  }, [search, status, fromDate, toDate]);

  useEffect(() => {
    const delay = setTimeout(fetchMeetings, 400);
    return () => clearTimeout(delay);
  }, [fetchMeetings]);

  const handleExportIcs = async (meeting) => {
    setExportingId(meeting.id);
    try {
      const { data } = await meetingsApi.exportIcs(meeting.id);
      const safeName = meeting.title.replace(/\s+/g, "_");
      downloadBlob(data, `${safeName}.ics`);
      toast("ICS file downloaded!", "success");
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setExportingId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Meetings</h1>
        <Link
          href="/dashboard/meetings/new"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          <PlusCircle className="w-4 h-4" /> New Meeting
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <div className="flex flex-wrap gap-3">
          {/* Search */}
          <div className="relative flex-1 min-w-48">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search meetings…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          {/* Status */}
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          {/* Date range */}
          <input
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            className="px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            className="px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* List */}
      {loading ? (
        <LoadingSpinner className="py-16" />
      ) : meetings.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
          <CalendarDays className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No meetings found</p>
          <Link
            href="/dashboard/meetings/new"
            className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
          >
            <PlusCircle className="w-4 h-4" /> Create Meeting
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {meetings.map((m) => (
            <div
              key={m.id}
              className="group bg-white rounded-xl border border-gray-100 shadow-sm hover:border-indigo-200 hover:shadow-md transition p-4 flex items-center gap-4"
            >
              {/* Date block */}
              <div className="flex-shrink-0 w-12 text-center hidden sm:block">
                <p className="text-xs text-gray-400 uppercase">
                  {new Date(m.start_time).toLocaleString("en", { month: "short" })}
                </p>
                <p className="text-xl font-bold text-indigo-600 leading-none">
                  {new Date(m.start_time).getDate()}
                </p>
              </div>

              {/* Info */}
              <Link
                href={`/dashboard/meetings/${m.id}`}
                className="flex-1 min-w-0"
              >
                <p className="font-semibold text-gray-900 truncate group-hover:text-indigo-700 transition">
                  {m.title}
                </p>
                <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1">
                  <span className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {formatDateTime(m.start_time)}
                  </span>
                  {m.location && (
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      <MapPin className="w-3 h-3" />
                      {m.location}
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-xs text-gray-500">
                    <Users className="w-3 h-3" />
                    {m.participant_count} participants
                  </span>
                </div>
              </Link>

              {/* Actions */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <span
                  className={`text-xs px-2 py-0.5 rounded-full font-medium ${getMeetingStatusColor(
                    m.status
                  )}`}
                >
                  {m.status}
                </span>
                <button
                  onClick={() => handleExportIcs(m)}
                  disabled={exportingId === m.id}
                  title="Export ICS"
                  className="p-1.5 rounded-lg text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition disabled:opacity-40"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
