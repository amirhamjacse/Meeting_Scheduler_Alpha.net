"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { meetingsApi } from "@/lib/api";
import { extractErrorMessage } from "@/lib/utils";
import { useToast } from "@/components/Toast";
import MeetingForm from "@/components/MeetingForm";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function NewMeetingPage() {
  const router = useRouter();
  const toast = useToast();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData) => {
    setLoading(true);
    try {
      const { data } = await meetingsApi.create(formData);
      toast("Meeting created successfully!", "success");
      router.push(`/dashboard/meetings/${data.id}`);
    } catch (err) {
      toast(extractErrorMessage(err), "error");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link
          href="/dashboard/meetings"
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Meeting</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Fill in the details and invite participants.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <MeetingForm onSubmit={handleSubmit} loading={loading} />
      </div>
    </div>
  );
}
