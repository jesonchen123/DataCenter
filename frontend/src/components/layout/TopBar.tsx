import { useState } from 'react'
import { Bell, HelpCircle, User, Shield } from 'lucide-react'

type Role = 'normal' | 'manager'

export function TopBar() {
  const [activeRole, setActiveRole] = useState<Role>('normal')

  return (
    <header
      className="flex items-center justify-between flex-shrink-0 px-6 border-b bg-white"
      style={{ height: 64, borderColor: '#e8e8e8' }}
    >
      {/* Left: title + greeting */}
      <div className="flex items-center gap-4">
        <h1
          className="font-semibold text-[16px]"
          style={{ color: '#1a1a2e', letterSpacing: '-0.01em' }}
        >
          工作台
        </h1>
        <span className="text-gray-400 text-[12px]">|</span>
        <span className="text-[13px]" style={{ color: '#999' }}>
          欢迎回来，张明
        </span>
      </div>

      {/* Right: role switcher + notifications + help */}
      <div className="flex items-center gap-2">
        <span className="text-[12px] mr-1" style={{ color: '#999' }}>
          角色切换：
        </span>

        {/* Normal User button */}
        <button
          onClick={() => setActiveRole('normal')}
          className="transition-all duration-200 px-4 py-[6px] rounded-md text-[13px] border cursor-pointer flex items-center"
          style={
            activeRole === 'normal'
              ? { background: '#0066CC', color: '#fff', borderColor: '#0066CC', fontWeight: 600 }
              : { borderColor: '#e0e0e0', background: '#fff', color: '#555', fontWeight: 500 }
          }
        >
          <User size={14} className="mr-1" />
          Normal User
        </button>

        {/* Manager button */}
        <button
          onClick={() => setActiveRole('manager')}
          className="transition-all duration-200 px-4 py-[6px] rounded-md text-[13px] border cursor-pointer flex items-center"
          style={
            activeRole === 'manager'
              ? { background: '#0066CC', color: '#fff', borderColor: '#0066CC', fontWeight: 600 }
              : { borderColor: '#e0e0e0', background: '#fff', color: '#555', fontWeight: 500 }
          }
        >
          <Shield size={14} className="mr-1" />
          Manager
        </button>

        {/* Notifications + Help */}
        <div
          className="ml-4 flex items-center gap-2 border-l pl-4"
          style={{ borderColor: '#e8e8e8' }}
        >
          <div className="relative cursor-pointer p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <Bell size={18} color="#666" />
            <span
              className="absolute top-1 right-1 flex items-center justify-center rounded-full text-white w-4 h-4 text-[10px] font-semibold"
              style={{ background: '#ff4d4f' }}
            >
              3
            </span>
          </div>
          <div className="p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
            <HelpCircle size={18} color="#666" />
          </div>
        </div>
      </div>
    </header>
  )
}
