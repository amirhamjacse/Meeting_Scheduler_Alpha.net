"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { meetingsApi } from "@/lib/api";
import { extractErrorMessage } from "@/lib/utils";
import { useToast } from "@/components/Toast";
import MeetingForm from "@/components/MeetingForm";
import LoadingSpinner from "@/components/LoadingSpinner";
import { ArrowLeft } from "lucide-react";

export default function EditMeetingPage() {
  const { id } = useParams();
  const router = useRouter();
  const toast = useToast();
  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    meetingsApi
      .get(id)
      .then(({ data }) => setMeeting(data))
      .catch((err) => {
        toast(extractErrorMessage(err), "error");
        router.push("/dashboard/meetings");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (formData) => {
    setSaving(true);
    try {
      await meetingsApi.update(id, formData);
      toast("Meeting updated!", "success");
      router.push(`/dashboard/meetings/${id}`);
    } catch (err) {
      toast(extractErrorMessage(err), "error");
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner className="py-24" size="lg" />;
  if (!meeting) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link
          href={`/dashboard/meetings/${id}`}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Meeting</h1>
          <p className="text-sm text-gray-500 mt-0.5 truncate">{meeting.title}</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <MeetingForm initial={meeting} onSubmit={handleSubmit} loading={saving} />
      </div>
    </div>
  );
}
