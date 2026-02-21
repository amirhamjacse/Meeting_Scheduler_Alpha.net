"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { meetingsApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/components/Toast";
import ParticipantList from "@/components/ParticipantList";
import LoadingSpinner from "@/components/LoadingSpinner";
import {
  formatDateTime,
  getMeetingStatusColor,
  downloadBlob,
  extractErrorMessage,
} from "@/lib/utils";
import {
  ArrowLeft,
  Edit2,
  Download,
  XCircle,
  Bell,
  Clock,
  MapPin,
  User,
  CalendarDays,
  Loader2,
  AlertTriangle,
} from "lucide-react";

export default function MeetingDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const toast = useToast();

  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [notifying, setNotifying] = useState(false);

  const fetchMeeting = async () => {
    try {
      const { data } = await meetingsApi.get(id);
      setMeeting(data);
    } catch (err) {
      toast(extractErrorMessage(err), "error");
      router.push("/dashboard/meetings");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeeting();
  }, [id]);

  const isOwner = user?.id === meeting?.created_by;

  const handleCancel = async () => {
    if (!confirm("Cancel this meeting? All participants will be notified.")) return;
    setCancelling(true);
    try {
      await meetingsApi.cancel(id);
      toast("Meeting cancelled.", "success");
      fetchMeeting();
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setCancelling(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const { data } = await meetingsApi.exportIcs(id);
      downloadBlob(data, `${meeting.title.replace(/\s+/g, "_")}.ics`);
      toast("ICS file downloaded!", "success");
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setExporting(false);
    }
  };

  const handleNotify = async (type) => {
    setNotifying(true);
    try {
      await meetingsApi.notify(id, type);
      toast(`${type} notifications sent!`, "success");
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setNotifying(false);
    }
  };

  if (loading) return <LoadingSpinner className="py-24" size="lg" />;
  if (!meeting) return null;

  const canCancel = isOwner && meeting.status === "scheduled";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top bar */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            href="/dashboard/meetings"
            className="mt-1 p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold text-gray-900">{meeting.title}</h1>
              <span
                className={`text-xs px-2.5 py-1 rounded-full font-semibold ${getMeetingStatusColor(
                  meeting.status
                )}`}
              >
                {meeting.status}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-0.5">
              Created by {meeting.created_by_email}
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition disabled:opacity-50"
          >
            {exporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            ICS
          </button>

          {isOwner && (
            <>
              <Link
                href={`/dashboard/meetings/${id}/edit`}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                <Edit2 className="w-4 h-4" /> Edit
              </Link>

              {canCancel && (
                <button
                  onClick={handleCancel}
                  disabled={cancelling}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition disabled:opacity-50"
                >
                  {cancelling ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <XCircle className="w-4 h-4" />
                  )}
                  Cancel
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-5">
          {/* Details card */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
            <h2 className="font-semibold text-gray-800">Meeting Details</h2>

            {meeting.description && (
              <p className="text-sm text-gray-600 leading-relaxed">
                {meeting.description}
              </p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <DetailItem icon={Clock} label="Start">
                {formatDateTime(meeting.start_time)}
              </DetailItem>
              <DetailItem icon={Clock} label="End">
                {formatDateTime(meeting.end_time)}
              </DetailItem>
              <DetailItem icon={CalendarDays} label="Duration">
                {meeting.duration_minutes} minutes
              </DetailItem>
              {meeting.location && (
                <DetailItem icon={MapPin} label="Location">
                  {meeting.location}
                </DetailItem>
              )}
              <DetailItem icon={User} label="Organiser">
                {meeting.created_by_email}
              </DetailItem>
            </div>
          </div>

          {/* Cancellation notice */}
          {meeting.status === "cancelled" && (
            <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              This meeting has been cancelled.
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-5">
          {/* Participants */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <ParticipantList
              meetingId={id}
              participants={meeting.participants || []}
              isOwner={isOwner}
              onRefresh={fetchMeeting}
            />
          </div>

          {/* Notifications (owner only) */}
          {isOwner && meeting.status === "scheduled" && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Bell className="w-4 h-4 text-indigo-500" /> Send Notification
              </h3>
              <div className="space-y-2">
                {["reminder", "update"].map((type) => (
                  <button
                    key={type}
                    onClick={() => handleNotify(type)}
                    disabled={notifying}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 capitalize transition disabled:opacity-50 flex items-center gap-2"
                  >
                    {notifying && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    Send {type}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailItem({ icon: Icon, label, children }) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
      <div>
        <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
        <p className="text-sm text-gray-700 font-medium">{children}</p>
      </div>
    </div>
  );
}
