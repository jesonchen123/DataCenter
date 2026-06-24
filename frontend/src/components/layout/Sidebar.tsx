import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Upload,
  Cpu,
  BookOpen,
  ClipboardCheck,
  Download,
  FileText,
  Settings,
  Database,
} from 'lucide-react'

const MAIN_MENU = [
  { to: '/dashboard', icon: LayoutDashboard, label: '总览', badge: null },
  { to: '/import', icon: Upload, label: '文档导入', badge: null },
  { to: '/tasks', icon: Cpu, label: '处理任务', badge: 8 },
  { to: '/knowledge', icon: BookOpen, label: '知识库', badge: null },
]

const WORKFLOW = [
  { to: '/review', icon: ClipboardCheck, label: '审核中心', badge: 5, badgeColor: '#faad14' },
  { to: '/export', icon: Download, label: '导出中心', badge: null },
  { to: '/audit', icon: FileText, label: '审计日志', badge: null },
]

export function Sidebar() {
  return (
    <aside
      className="flex flex-col flex-shrink-0 h-screen overflow-hidden"
      style={{ width: 240, background: '#1a1a2e', color: '#c0c0d0' }}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-700/40">
        <div
          className="flex items-center justify-center rounded-lg"
          style={{ width: 36, height: 36, background: '#0066CC' }}
        >
          <Database size={20} color="#fff" />
        </div>
        <div>
          <span
            className="text-white font-semibold tracking-tight"
            style={{ fontSize: 17, letterSpacing: '-0.01em' }}
          >
            数据中台
          </span>
          <p className="text-gray-500" style={{ fontSize: 10, marginTop: -1 }}>
            Data Middle Platform
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {/* 主菜单 */}
        <div
          className="px-6 mb-3"
          style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#666' }}
        >
          主菜单
        </div>
        {MAIN_MENU.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar-item flex items-center gap-3 ${isActive ? 'active' : ''}`
            }
          >
            <item.icon size={18} />
            <span style={{ fontSize: 14 }}>{item.label}</span>
            {item.badge != null && (
              <span
                className="ml-auto flex items-center justify-center rounded-full text-white font-semibold"
                style={{ width: 20, height: 20, fontSize: 11, background: '#0066CC' }}
              >
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}

        {/* 工作流 */}
        <div
          className="px-6 mt-6 mb-3"
          style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#666' }}
        >
          工作流
        </div>
        {WORKFLOW.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar-item flex items-center gap-3 ${isActive ? 'active' : ''}`
            }
          >
            <item.icon size={18} />
            <span style={{ fontSize: 14 }}>{item.label}</span>
            {item.badge != null && (
              <span
                className="ml-auto flex items-center justify-center rounded-full font-semibold"
                style={{
                  width: 20,
                  height: 20,
                  fontSize: 11,
                  background: item.badgeColor || '#0066CC',
                  color: item.badgeColor ? '#1a1a2e' : '#fff',
                }}
              >
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Footer */}
      <div className="px-4 py-4 border-t border-gray-700/40">
        <div
          className="flex items-center gap-3 px-2 py-3 rounded-lg cursor-pointer transition-colors duration-200 hover:bg-white/[0.08]"
          style={{ background: 'rgba(255,255,255,0.04)' }}
        >
          <div
            className="flex items-center justify-center rounded-full text-white"
            style={{ width: 32, height: 32, background: '#555', fontSize: 13, fontWeight: 600 }}
          >
            张
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white truncate" style={{ fontSize: 13, fontWeight: 500 }}>
              张明
            </p>
            <p className="truncate" style={{ fontSize: 11, color: '#888' }}>
              normal_user
            </p>
          </div>
          <NavLink
            to="/settings"
            className="p-1 rounded-md hover:bg-white/10 transition-colors flex items-center justify-center"
          >
            <Settings size={16} color="#777" />
          </NavLink>
        </div>
      </div>
    </aside>
  )
}
