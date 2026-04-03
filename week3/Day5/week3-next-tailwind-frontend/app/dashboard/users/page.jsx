"use client";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";

export default function UsersPage() {
  const users = [
    {
      id: 1,
      name: "Vibhav Khaneja",
      email: "vibhav.khaneja@hestabit.com",
      role: "Trainee Software Engineer",
      time: "10:45 AM",
      verdict: "On-time",
    },
    {
      id: 2,
      name: "Abhishek Rai",
      email: "abhishek.com",
      role: "Trainee Software Engineer",
      time: "11:42 AM",
      verdict: "Late",
    },
    {
      id: 3,
      name: "Sahil Batra",
      email: "sahil.com",
      role: "DevOps Intern",
      time: "09:48 AM",
      verdict: "On-time",
    },
    {
      id: 4,
      name: "Ishika Sharma",
      email: "ishika.in",
      time: "12:10 PM",
      role: "HR",
      verdict: "Late",
    },
    {
      id: 5,
      name: "Shubh Mishra",
      email: "shubh.com",
      time: "10:55 AM",
      role: "Developer",
      verdict: "On-time",
    },
    {
      id: 6,
      name: "Gautam Gulati",
      email: "gauti.in",
      time: "10:23 AM",
      role: "Trainee Software Engineer",
      verdict: "On-time",
    },
    {
      id: 7,
      name: "Naina Yadav",
      email: "naina.com",
      time: "12:03 PM",
      role: "Developer",
      verdict: "late",
    },
    {
      id: 8,
      name: "Pramod Mathur",
      email: "mathur.com",
      time: "01:55 PM",
      role: "HR",
      verdict: "late",
    },
    {
      id: 9,
      name: "Muskan Das",
      email: "muskan.com",
      time: "12:38 PM",
      role: "Assosiciate Software Engineer",
      verdict: "late",
    },
    {
      id: 10,
      name: "Apoorv Bansal",
      email: "Apooorv.com",
      time: "10:12 AM",
      role: "Developer",
      verdict: "On-time",
    },
  ];

  return (
    <div className="p-8 bg-white min-h-screen">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Users Attendance
          </h1>
        </div>

        <div className="w-full md:w-72">
          <div className="relative">

            <Input
              placeholder="Search users..."
              className="bg-slate-50 border-slate-200 focus:bg-white transition-all"
            />
          </div>
        </div>
      </div>
      
      <div className="overflow-hidden border border-slate-200 rounded-xl shadow-sm bg-white">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">
                Name
              </th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">
                Email
              </th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">
                Role
              </th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">
                Punch-In Time
              </th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500 text-center">
                Verdict
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <td className="p-4 text-sm font-semibold text-slate-700">
                  {user.name}
                </td>
                <td className="p-4 text-sm text-slate-500">{user.email}</td>
                <td className="p-4 text-sm text-slate-500">{user.role}</td>
                <td className="p-4 text-sm font-mono text-slate-600">
                  {user.time}
                </td>
                <td className="p-4 text-center">
                  <Badge
                    variant={user.verdict === "On-time" ? "success" : "danger"}
                  >
                    {user.verdict}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>


        <div className="p-4 bg-slate-50 flex items-center justify-between border-t border-slate-200 text-xs font-bold text-slate-500 uppercase tracking-widest">
          <span>Showing {users.length} of 12 entries</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 border border-slate-200 rounded hover:bg-white transition-all">
              Prev
            </button>
            <button className="px-3 py-1 bg-slate-900 text-white rounded">
              1
            </button>
            <button className="px-3 py-1 border border-slate-200 rounded hover:bg-white transition-all">
              2
            </button>
            <button className="px-3 py-1 border border-slate-200 rounded hover:bg-white transition-all">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
