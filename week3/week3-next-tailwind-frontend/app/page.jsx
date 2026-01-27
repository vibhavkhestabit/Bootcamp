'use client';
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";
import { useState } from 'react';

export default function DashboardPage() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="space-y-8">
      {/* 1. Hestabit Dashboard Header & Metrics */}
      <section>
        {/* Header Bar with Heading and Button */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Hestabit Dashboard</h1>
            <p className="text-slate-500 text-sm">Real-time Operational Overview</p>
          </div>
          
          {/* Shifted Modal Button here and Renamed */}
          <Button variant="primary" onClick={() => setIsOpen(true)}>
            Download Report
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card title="Project Pipeline" color="primary" footer="View Project Details">
            12 Active
          </Card>

          <Card title="Tickets Raised" color="warning" footer="View Support Desk">
            24 Open
          </Card>

          <Card title="Monthly Revenue" color="success" footer="View Financials">
            $142,500
          </Card>

          <Card title="Absenteeism Rate" color="danger" footer="View Attendance Log">
            3.2%
          </Card>
        </div>
      </section>

      <hr className="border-slate-200" />

      {/* 2. Component Sandbox (Kept for testing other elements) */}
      <section className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-slate-700">Component Sandbox</h2>
        <div className="flex flex-wrap items-center gap-6">
          <div className="flex gap-2">
            <Badge variant="success">Active</Badge>
            <Badge variant="warning">This Month</Badge>
          </div>
          <div className="flex gap-3">
            <Button variant="secondary">Secondary Action</Button>
            <Button variant="danger">Delete Data</Button>
          </div>
        </div>
      </section>

      <Modal open={isOpen} title="Report Download System" onClose={() => setIsOpen(false)}>
        <p className="text-slate-600">The report generation module is currently being tested. This modal confirms the trigger is working!</p>
      </Modal>
    </div>
  );
}