import Link from 'next/link';
import Button from "@/components/ui/Button";

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">About Hestabit</h1>
        <p className="text-slate-600 leading-relaxed mb-6">
          Hestabit is a leading technology solutions provider. This dashboard is designed 
          to streamline internal operations, track project health, and monitor revenue 
          growth in real-time.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h3 className="font-semibold text-blue-900">Our Mission</h3>
            <p className="text-sm text-blue-700">To empower businesses through scalable and innovative software solutions.</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-100">
            <h3 className="font-semibold text-green-900">Our Vision</h3>
            <p className="text-sm text-green-700">Being the global benchmark for excellence in digital transformation.</p>
          </div>
        </div>

        <Link href="/dashboard">
          <Button variant="secondary">Back to Dashboard</Button>
        </Link>
      </section>
    </div>
  );
}