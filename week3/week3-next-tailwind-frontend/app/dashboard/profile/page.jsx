'use client';
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";

export default function ProfilePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">User Profile</h1>
          <p className="text-slate-500 text-sm">Manage your account settings and personal information</p>
        </div>
        <Button variant="secondary">Edit Profile</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Profile Summary */}
        <Card title="Account Overview" color="primary">
          <div className="flex flex-col items-center py-4 text-center">
            <div className="w-24 h-24 rounded-full bg-slate-200 flex items-center justify-center text-3xl mb-4 border-4 border-white shadow-sm">
              👤
            </div>
            <h2 className="text-xl font-bold text-slate-800">Hestabit Admin</h2>
            <p className="text-sm text-slate-500 mb-4">admin@hestabit.com</p>
            <div className="flex gap-2">
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded">Verified</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded">Admin</span>
            </div>
          </div>
        </Card>

        {/* Right Column: Detailed Info - Fixed with color prop */}
        <div className="md:col-span-2">
          <Card title="Personal Information" color="primary">
            <div className="space-y-4 text-sm">
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-slate-500 font-medium">Full Name</span>
                <span className="text-slate-800 font-semibold">Hestabit Operations Team</span>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-slate-500 font-medium">Role</span>
                <span className="text-slate-800 font-semibold">Project Manager</span>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-slate-500 font-medium">Department</span>
                <span className="text-slate-800 font-semibold">Software Development</span>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-slate-500 font-medium">Location</span>
                <span className="text-slate-800 font-semibold">Noida, India</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Joined Date</span>
                <span className="text-slate-800 font-semibold">January 2026</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}