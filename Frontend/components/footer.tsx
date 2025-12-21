import { MapPin, Mail, Phone, GraduationCap, Building2 } from "lucide-react"

export function Footer() {
  return (
    <footer className="relative z-10 border-t border-purple-500/20 bg-slate-950/95 backdrop-blur-xl mt-auto">
      <div className="container mx-auto px-4 py-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
          {/* Project Info */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-purple-400" />
              Smart Parking System
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              AI-Powered Real-Time Parking Monitoring & Management Solution
            </p>
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>System Online</span>
            </div>
          </div>

          {/* College Information */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-purple-400" />
              Academic Institution
            </h3>
            <div className="space-y-2 text-sm text-slate-300">
              <p className="font-medium text-white">College of Science and Technology</p>
              <p className="leading-relaxed">
                Advancing innovation through practical solutions in Computer Science and Engineering
              </p>
            </div>
          </div>

          {/* Contact & Credits */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-purple-400" />
              Project Credits
            </h3>
            <div className="space-y-2 text-sm text-slate-300">
              <p className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-purple-400" />
                <span>Collaborative project by <span className="font-medium text-white">EDRUK</span> & <span className="font-medium text-white">CST</span></span>
              </p>
              <p className="text-xs leading-relaxed">
                Under the provision of <span className="font-medium text-white">GovTech</span>
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-purple-500/20">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3">
            <p className="text-slate-300 text-xs text-center md:text-left">
              © {new Date().getFullYear()} Smart Parking System. A collaborative project by EDRUK and College of Science and Technology under GovTech provision.
            </p>
            <p className="text-slate-400 text-xs text-center md:text-right">
              Real-time updates • AI-Powered Detection • Secure Platform
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
