import Link from 'next/link';
import Button from "@/components/ui/Button";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 p-6 text-center">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">Welcome to Hestabit</h1>
      <p className="text-lg text-slate-600 mb-8 max-w-md">
        Your internal hub for project management, revenue tracking, and operations.
      </p>
      
      {/* Link helps navigate to the dashboard folder without a full page reload */}
      <Link href="/dashboard">
        <Button variant="primary">Go to Dashboard</Button>
      </Link>
    </div>
  );
}