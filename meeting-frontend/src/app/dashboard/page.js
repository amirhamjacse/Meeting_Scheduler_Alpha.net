"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { meetingsApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import {
  formatDateTime,
  getMeetingStatusColor,
  getMeetingDayLabel,
} from "@/lib/utils";
import LoadingSpinner from "@/components/LoadingSpinner";
import {
  CalendarDays,
  Clock,
  MapPin,
  Users,
  PlusCircle,
  TrendingUp,
  CheckCircle2,
  XCircle,
} from "lucide-react";

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  );
}

function UpcomingCard({ meeting }) {
  return (
    <Link
      href={`/dashboard/meetings/${meeting.id}`}
      className="group flex items-start gap-4 p-4 bg-white rounded-xl border border-gray-100 shadow-sm hover:border-indigo-200 hover:shadow-md transition"
    >
      <div className="flex-shrink-0 w-12 text-center">
        <p className="text-xs text-gray-400 uppercase tracking-wide">
          {new Date(meeting.start_time)
            .toLocaleString("en", { month: "short" })
            .toUpperCase()}
        </p>
        <p className="text-xl font-bold text-indigo-600 leading-none">
          {new Date(meeting.start_time).getDate()}
        </p>
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-gray-900 truncate group-hover:text-indigo-700 transition">
          {meeting.title}
        </p>
        <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1">
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            {new Date(meeting.start_time).toLocaleTimeString("en", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          {meeting.location && (
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <MapPin className="w-3 h-3" />
              {meeting.location}
            </span>
          )}
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Users className="w-3 h-3" />
            {meeting.participant_count}
          </span>
        </div>
      </div>
      <span
        className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${getMeetingStatusColor(
          meeting.status
        )}`}
      >
        {meeting.status}
      </span>
    </Link>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    meetingsApi
      .list({ ordering: "start_time" })
      .then(({ data }) => setMeetings(data.results ?? data))
      .finally(() => setLoading(false));
  }, []);

  const now = new Date();
  const upcoming = meetings.filter(
    (m) => m.status === "scheduled" && new Date(m.start_time) >= now
  );
  const completed = meetings.filter((m) => m.status === "completed");
  const cancelled = meetings.filter((m) => m.status === "cancelled");

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Good {getTimeOfDay()},{" "}
          {user?.username || user?.email?.split("@")[0]} 👋
        </h1>
        <p className="text-gray-500 mt-1">
          Here&apos;s what&apos;s on your schedule.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={CalendarDays}
          label="Total Meetings"
          value={meetings.length}
          color="bg-indigo-500"
        />
        <StatCard
          icon={TrendingUp}
          label="Upcoming"
          value={upcoming.length}
          color="bg-blue-500"
        />
        <StatCard
          icon={CheckCircle2}
          label="Completed"
          value={completed.length}
          color="bg-emerald-500"
        />
        <StatCard
          icon={XCircle}
          label="Cancelled"
          value={cancelled.length}
          color="bg-red-400"
        />
      </div>

      {/* Upcoming Meetings */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Upcoming Meetings</h2>
          <Link
            href="/dashboard/meetings/new"
            className="flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 transition"
          >
            <PlusCircle className="w-4 h-4" /> New Meeting
          </Link>
        </div>

        {loading ? (
          <LoadingSpinner className="py-12" />
        ) : upcoming.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-200">
            <CalendarDays className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No upcoming meetings</p>
            <p className="text-sm text-gray-400 mt-1">
              Create your first meeting to get started.
            </p>
            <Link
              href="/dashboard/meetings/new"
              className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
            >
              <PlusCircle className="w-4 h-4" /> New Meeting
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {upcoming.slice(0, 8).map((m) => (
              <UpcomingCard key={m.id} meeting={m} />
            ))}
            {upcoming.length > 8 && (
              <Link
                href="/dashboard/meetings"
                className="block text-center text-sm text-indigo-600 hover:underline py-2"
              >
                View all {upcoming.length} upcoming meetings →
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function getTimeOfDay() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
