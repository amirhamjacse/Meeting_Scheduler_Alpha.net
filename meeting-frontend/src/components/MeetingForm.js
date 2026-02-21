"use client";

import { useState, useEffect } from "react";
import { meetingsApi } from "@/lib/api";
import { toLocalInputValue, extractErrorMessage } from "@/lib/utils";
import { useToast } from "@/components/Toast";
import { AlertTriangle, Plus, Trash2, Loader2 } from "lucide-react";

const EMPTY_PARTICIPANT = { email: "", name: "" };

export default function MeetingForm({ initial = null, onSubmit, loading }) {
  const toast = useToast();
  const [form, setForm] = useState({
    title: initial?.title || "",
    description: initial?.description || "",
    location: initial?.location || "",
    start_time: toLocalInputValue(initial?.start_time) || "",
    end_time: toLocalInputValue(initial?.end_time) || "",
    status: initial?.status || "scheduled",
    participants: [],
  });

  const [participants, setParticipants] = useState(
    initial?.participants?.map((p) => ({ email: p.email, name: p.name || "" })) || [
      EMPTY_PARTICIPANT,
    ]
  );

  const [conflicts, setConflicts] = useState({});
  const [checkingConflicts, setCheckingConflicts] = useState(false);

  // ── Conflict check whenever times or participant emails change ──────────
  useEffect(() => {
    const emails = participants
      .map((p) => p.email.trim())
      .filter((e) => e.includes("@"));
    if (!form.start_time || !form.end_time || emails.length === 0) {
      setConflicts({});
      return;
    }
    const delay = setTimeout(async () => {
      setCheckingConflicts(true);
      try {
        const { data } = await meetingsApi.checkConflicts({
          start_time: new Date(form.start_time).toISOString(),
          end_time: new Date(form.end_time).toISOString(),
          participant_emails: emails,
          ...(initial?.id ? { exclude_meeting_id: initial.id } : {}),
        });
        setConflicts(data.conflicts || {});
      } catch (_) {}
      setCheckingConflicts(false);
    }, 600);
    return () => clearTimeout(delay);
  }, [form.start_time, form.end_time, participants, initial?.id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleParticipantChange = (index, field, value) => {
    setParticipants((prev) =>
      prev.map((p, i) => (i === index ? { ...p, [field]: value } : p))
    );
  };

  const addParticipant = () =>
    setParticipants((prev) => [...prev, { ...EMPTY_PARTICIPANT }]);

  const removeParticipant = (index) =>
    setParticipants((prev) => prev.filter((_, i) => i !== index));

  const handleSubmit = (e) => {
    e.preventDefault();
    const validParticipants = participants.filter((p) =>
      p.email.trim().includes("@")
    );
    onSubmit({ ...form, participants: validParticipants });
  };

  const inputCls =
    "w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition";
  const labelCls = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div>
        <label className={labelCls}>Title *</label>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          required
          placeholder="Team Standup"
          className={inputCls}
        />
      </div>

      {/* Description */}
      <div>
        <label className={labelCls}>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          rows={3}
          placeholder="Meeting agenda and notes…"
          className={inputCls}
        />
      </div>

      {/* Location */}
      <div>
        <label className={labelCls}>Location</label>
        <input
          name="location"
          value={form.location}
          onChange={handleChange}
          placeholder="Conference Room A / Zoom link"
          className={inputCls}
        />
      </div>

      {/* Date/Time */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelCls}>Start Time *</label>
          <input
            type="datetime-local"
            name="start_time"
            value={form.start_time}
            onChange={handleChange}
            required
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>End Time *</label>
          <input
            type="datetime-local"
            name="end_time"
            value={form.end_time}
            onChange={handleChange}
            required
            className={inputCls}
          />
        </div>
      </div>

      {/* Status (edit only) */}
      {initial && (
        <div>
          <label className={labelCls}>Status</label>
          <select
            name="status"
            value={form.status}
            onChange={handleChange}
            className={inputCls}
          >
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      )}

      {/* Participants */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className={labelCls.replace(" mb-1", "")}>Participants</label>
          {checkingConflicts && (
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <Loader2 className="w-3 h-3 animate-spin" /> Checking conflicts…
            </span>
          )}
        </div>

        {/* Conflict warnings */}
        {Object.keys(conflicts).length > 0 && (
          <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg space-y-1">
            <div className="flex items-center gap-2 text-amber-700 font-medium text-sm">
              <AlertTriangle className="w-4 h-4" /> Scheduling Conflicts Detected
            </div>
            {Object.entries(conflicts).map(([email, meetings]) => (
              <div key={email} className="text-xs text-amber-600">
                <span className="font-medium">{email}</span> conflicts with:{" "}
                {meetings.map((m) => m.title).join(", ")}
              </div>
            ))}
          </div>
        )}

        <div className="space-y-2">
          {participants.map((p, i) => (
            <div key={i} className="flex gap-2 items-center">
              <input
                type="email"
                placeholder="email@example.com"
                value={p.email}
                onChange={(e) => handleParticipantChange(i, "email", e.target.value)}
                className={`${inputCls} flex-1`}
              />
              <input
                type="text"
                placeholder="Name (optional)"
                value={p.name}
                onChange={(e) => handleParticipantChange(i, "name", e.target.value)}
                className={`${inputCls} w-36`}
              />
              <button
                type="button"
                onClick={() => removeParticipant(i)}
                disabled={participants.length === 1}
                className="p-2 text-gray-400 hover:text-red-500 disabled:opacity-30 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={addParticipant}
          className="mt-2 flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800 transition"
        >
          <Plus className="w-4 h-4" /> Add participant
        </button>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg disabled:opacity-60 transition flex items-center justify-center gap-2"
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        {initial ? "Save Changes" : "Create Meeting"}
      </button>
    </form>
  );
}
