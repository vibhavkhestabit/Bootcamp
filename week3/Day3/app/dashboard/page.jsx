'use client';
import { useState } from 'react';
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";


import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

export default function DashboardPage() {
  const [isOpen, setIsOpen] = useState(false);

const users = [
    { id: 1, name: "Vibhav Khaneja", email: "vibhav.khaneja@hestabit.com", role: "Trainee Software Engineer", time: "10:45 AM", verdict: "On-time" },
    { id: 2, name: "Abhishek Rai", email: "abhishek.com", role: "Trainee Software Engineer", time: "11:42 AM", verdict: "Late" },
    { id: 3, name: "Sahil Batra", email: "sahil.com", role: "DevOps Intern", time: "09:48 AM", verdict: "On-time" },
    { id: 4, name: "Ishika Sharma", email: "ishika.in", role: "HR", time: "12:10 PM", verdict: "Late" },
    { id: 5, name: "Shubh Mishra", email: "shubh.com", role: "Developer", time: "10:55 AM", verdict: "On-time" },
  ];

  // 1. AREA CHART (Line with Filler) Data
  const areaData = {
    labels: ['Mar 1', 'Mar 3', 'Mar 5', 'Mar 7', 'Mar 9', 'Mar 11', 'Mar 13'],
    datasets: [
      {
        fill: true,
        label: 'Efficiency',
        data: [12000, 28000, 24000, 35000, 29000, 33000, 42000],
        borderColor: '#3666b4ff',
        backgroundColor: 'rgba(9, 66, 159, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const areaOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 2000, easing: 'easeInOutQuart' },
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 10 } } },
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    },
  };

  // 2. BAR CHART Data
  const barData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [4500, 5200, 4900, 7200, 8100, 13500],
        backgroundColor: '#2d589aff',
        borderRadius: 4,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 2000, delay: 500 },
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 10 } } },
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    },
  };

  return (
    <div className="space-y-8 p-6">
      
      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Hestabit Dashboard</h1>
          </div>
          <Button variant="primary" onClick={() => setIsOpen(true)}>
            Download Report
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card title="Project Pipeline" color="primary" footer="View Project Details">12 Active</Card>
          <Card title="Tickets Raised" color="warning" footer="View Support Desk">24 Open</Card>
          <Card title="Monthly Revenue" color="success" footer="View Financials">$142,500</Card>
          <Card title="Absenteeism Rate" color="danger" footer="View Attendance Log">3.2%</Card>
        </div>
      </section>

      {/* NEW: CHART.JS ANALYTICS SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm h-[380px]">
          <h3 className="text-xs font-black text-slate-700 uppercase tracking-widest mb-6 border-b border-slate-50 pb-2">
            Area Chart Example
          </h3>
          <div className="h-[280px]">
            <Line data={areaData} options={areaOptions} />
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm h-[380px]">
          <h3 className="text-xs font-black text-slate-700 uppercase tracking-widest mb-6 border-b border-slate-50 pb-2">
            Bar Chart Example
          </h3>
          <div className="h-[280px]">
            <Bar data={barData} options={barOptions} />
          </div>
        </div>
      </div>

      <hr className="border-slate-200" />

      <section className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-800">User Activity Logs</h2>
          <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Real-time punctuality tracking</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-[10px] font-black uppercase text-slate-500 tracking-widest">
              <tr>
                <th className="p-4">Name</th>
                <th className="p-4">Role</th>
                <th className="p-4">Punch-In</th>
                <th className="p-4 text-center">Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="p-4 text-sm font-semibold text-slate-700">{user.name}</td>
                  <td className="p-4 text-xs text-slate-500">{user.role}</td>
                  <td className="p-4 text-xs font-mono text-slate-600">{user.time}</td>
                  <td className="p-4 text-center">
                    <Badge variant={user.verdict === "On-time" ? "success" : "danger"}>{user.verdict}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Modal open={isOpen} title="Report Download System" onClose={() => setIsOpen(false)}>
        <p className="text-slate-600">The report generation module is currently being tested. This modal confirms the trigger is working!</p>
      </Modal>
    </div>
  );
}