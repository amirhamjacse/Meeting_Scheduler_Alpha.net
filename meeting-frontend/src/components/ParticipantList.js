"use client";

import { useState } from "react";
import { participantsApi } from "@/lib/api";
import { getParticipantStatusColor, extractErrorMessage } from "@/lib/utils";
import { useToast } from "@/components/Toast";
import { Trash2, UserPlus, Loader2, Mail } from "lucide-react";

export default function ParticipantList({ meetingId, participants = [], isOwner, onRefresh }) {
  const toast = useToast();
  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");
  const [adding, setAdding] = useState(false);
  const [removingId, setRemovingId] = useState(null);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newEmail.trim()) return;
    setAdding(true);
    try {
      await participantsApi.add(meetingId, {
        email: newEmail.trim(),
        name: newName.trim(),
      });
      toast("Participant added and invitation sent.", "success");
      setNewEmail("");
      setNewName("");
      onRefresh?.();
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setAdding(false);
    }
  };

  const handleRemove = async (id) => {
    if (!confirm("Remove this participant?")) return;
    setRemovingId(id);
    try {
      await participantsApi.remove(meetingId, id);
      toast("Participant removed.", "success");
      onRefresh?.();
    } catch (err) {
      toast(extractErrorMessage(err), "error");
    } finally {
      setRemovingId(null);
    }
  };

  return (
    <div>
      <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <Mail className="w-4 h-4 text-indigo-500" />
        Participants ({participants.length})
      </h3>

      <ul className="space-y-2 mb-4">
        {participants.length === 0 && (
          <li className="text-sm text-gray-400 italic">No participants yet.</li>
        )}
        {participants.map((p) => (
          <li
            key={p.id}
            className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg border border-gray-100"
          >
            <div>
              <p className="text-sm font-medium text-gray-800">
                {p.name || p.email}
              </p>
              {p.name && (
                <p className="text-xs text-gray-500">{p.email}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${getParticipantStatusColor(
                  p.status
                )}`}
              >
                {p.status}
              </span>
              {isOwner && (
                <button
                  onClick={() => handleRemove(p.id)}
                  disabled={removingId === p.id}
                  className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50 transition"
                >
                  {removingId === p.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5" />
                  )}
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {/* Add participant (owner only) */}
      {isOwner && (
        <form onSubmit={handleAdd} className="flex gap-2 flex-wrap">
          <input
            type="email"
            required
            placeholder="email@example.com"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            className="flex-1 min-w-40 px-3 py-1.5 text-sm rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            type="text"
            placeholder="Name (optional)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="w-36 px-3 py-1.5 text-sm rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={adding}
            className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-60 flex items-center gap-1 transition"
          >
            {adding ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <UserPlus className="w-4 h-4" />
            )}
            Add
          </button>
        </form>
      )}
    </div>
  );
}
