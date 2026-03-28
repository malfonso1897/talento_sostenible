import SwiftUI
import CoreData

struct DashboardView: View {
    @Environment(\.managedObjectContext) private var context

    @FetchRequest(sortDescriptors: []) private var contacts: FetchedResults<CDContact>
    @FetchRequest(sortDescriptors: []) private var companies: FetchedResults<CDCompany>
    @FetchRequest(sortDescriptors: []) private var leads: FetchedResults<CDLead>
    @FetchRequest(sortDescriptors: []) private var opportunities: FetchedResults<CDOpportunity>
    @FetchRequest(sortDescriptors: []) private var tickets: FetchedResults<CDTicket>
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDActivity.dueDate, ascending: true)],
        predicate: NSPredicate(format: "isCompleted == NO")
    ) private var pendingActivities: FetchedResults<CDActivity>

    @StateObject private var intelligence = CRMIntelligence()

    var openOpportunities: [CDOpportunity] {
        opportunities.filter { $0.stage != "closed_won" && $0.stage != "closed_lost" }
    }

    var pipelineValue: Double {
        openOpportunities.reduce(0) { $0 + $1.amount }
    }

    var openTickets: Int {
        tickets.filter { $0.status == "open" || $0.status == "in_progress" }.count
    }

    var todayActivities: [CDActivity] {
        let cal = Foundation.Calendar.current
        return pendingActivities.filter { a in
            guard let d = a.dueDate else { return false }
            return cal.isDateInToday(d)
        }
    }

    var overdueActivities: [CDActivity] {
        pendingActivities.filter { a in
            guard let d = a.dueDate else { return false }
            return d < Date()
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header con resumen rapido
                HStack(alignment: .top) {
                    VStack(alignment: .leading) {
                        Text("Dashboard")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        Text(todayGreeting())
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                    // Indicador de alertas
                    if !intelligence.alerts.isEmpty {
                        VStack(alignment: .trailing, spacing: 2) {
                            Text("\(intelligence.alerts.count)")
                                .font(.system(size: 28, weight: .bold))
                                .foregroundColor(alertsMainColor())
                            Text("alertas activas")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(alertsMainColor().opacity(0.1))
                        .cornerRadius(10)
                    }
                }

                // KPIs
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 16) {
                    KPICard(title: "Contactos", value: "\(contacts.count)", subtitle: "\(companies.count) empresas", color: .blue)
                    KPICard(title: "Leads", value: "\(leads.count)", subtitle: "activos", color: .orange)
                    KPICard(title: "Oportunidades", value: "\(openOpportunities.count)", subtitle: String(format: "%.0f EUR pipeline", pipelineValue), color: .green)
                    KPICard(title: "Tickets", value: "\(openTickets)", subtitle: "abiertos", color: .red)
                    KPICard(title: "Hoy", value: "\(todayActivities.count)", subtitle: "\(overdueActivities.count) vencidas", color: .purple)
                }

                // MARK: - Centro de alertas inteligente
                if !intelligence.alerts.isEmpty {
                    GroupBox {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Centro de alertas")
                                    .font(.headline)
                                    .fontWeight(.bold)
                                Spacer()
                                Text("\(intelligence.alerts.filter { $0.priority == .critical }.count) criticas")
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                                    .background(Color.red.opacity(0.15))
                                    .foregroundColor(.red)
                                    .cornerRadius(8)
                                Text("\(intelligence.alerts.filter { $0.priority == .high }.count) altas")
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                                    .background(Color.orange.opacity(0.15))
                                    .foregroundColor(.orange)
                                    .cornerRadius(8)
                            }

                            ForEach(intelligence.alerts.prefix(8)) { alert in
                                HStack(spacing: 10) {
                                    // Indicador de prioridad
                                    Circle()
                                        .fill(alertColor(alert.priority))
                                        .frame(width: 10, height: 10)

                                    // Icono segun tipo
                                    Text(alertIcon(alert.type))
                                        .font(.system(size: 14))
                                        .frame(width: 24)

                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(alert.title)
                                            .fontWeight(.medium)
                                            .lineLimit(1)
                                        Text(alert.detail)
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                            .lineLimit(1)
                                    }
                                    Spacer()
                                    Text(alert.priority.label)
                                        .font(.caption2)
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(alertColor(alert.priority).opacity(0.15))
                                        .foregroundColor(alertColor(alert.priority))
                                        .cornerRadius(6)
                                }
                                .padding(.vertical, 4)
                                if alert.id != intelligence.alerts.prefix(8).last?.id {
                                    Divider()
                                }
                            }

                            if intelligence.alerts.count > 8 {
                                Text("+ \(intelligence.alerts.count - 8) alertas mas")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .padding(.top, 4)
                            }
                        }
                    }
                }

                // MARK: - Que hacer hoy
                GroupBox {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Que hacer hoy")
                            .font(.headline)
                            .fontWeight(.bold)

                        if todayActivities.isEmpty && overdueActivities.isEmpty {
                            Text("No hay tareas para hoy - Buen momento para revisar leads y oportunidades")
                                .foregroundColor(.secondary)
                                .padding(.vertical, 8)
                        } else {
                            // Actividades vencidas primero
                            ForEach(overdueActivities.prefix(5)) { activity in
                                activityRow(activity, isOverdue: true)
                            }
                            // Actividades de hoy
                            ForEach(todayActivities.prefix(5)) { activity in
                                activityRow(activity, isOverdue: false)
                            }
                        }
                    }
                }

                // MARK: - Pipeline y leads lado a lado
                HStack(alignment: .top, spacing: 16) {
                    // Proximas oportunidades
                    GroupBox("Oportunidades activas") {
                        if openOpportunities.isEmpty {
                            Text("No hay oportunidades activas")
                                .foregroundColor(.secondary)
                                .padding()
                        } else {
                            ForEach(openOpportunities.prefix(5)) { opp in
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(opp.name ?? "")
                                            .fontWeight(.medium)
                                        HStack(spacing: 8) {
                                            Text(String(format: "%.0f EUR", opp.amount))
                                                .font(.caption)
                                                .foregroundColor(.green)
                                            if let date = opp.expectedCloseDate {
                                                Text(date, style: .date)
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                            }
                                        }
                                    }
                                    Spacer()
                                    StatusBadge(text: opp.stage ?? "", color: stageColor(opp.stage ?? ""))
                                }
                                .padding(.vertical, 4)
                                Divider()
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)

                    // Leads recientes
                    GroupBox("Leads recientes") {
                        if leads.isEmpty {
                            Text("No hay leads")
                                .foregroundColor(.secondary)
                                .padding()
                        } else {
                            ForEach(Array(leads.prefix(5))) { lead in
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("\(lead.firstName ?? "") \(lead.lastName ?? "")")
                                            .fontWeight(.medium)
                                        HStack(spacing: 8) {
                                            Text(lead.companyName ?? "")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                            Text("Score: \(lead.score)")
                                                .font(.caption)
                                                .foregroundColor(lead.score > 70 ? .green : .secondary)
                                        }
                                    }
                                    Spacer()
                                    StatusBadge(text: lead.status ?? "new", color: leadStatusColor(lead.status ?? "new"))
                                }
                                .padding(.vertical, 4)
                                Divider()
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .padding()
        }
        .onAppear {
            intelligence.analyze(context: context)
        }
    }

    // MARK: - Helpers

    private func todayGreeting() -> String {
        let hour = Foundation.Calendar.current.component(.hour, from: Date())
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "es_ES")
        formatter.dateFormat = "EEEE d 'de' MMMM"
        let dateStr = formatter.string(from: Date()).capitalized

        if hour < 12 { return "Buenos dias - \(dateStr)" }
        if hour < 20 { return "Buenas tardes - \(dateStr)" }
        return "Buenas noches - \(dateStr)"
    }

    @ViewBuilder
    private func activityRow(_ activity: CDActivity, isOverdue: Bool) -> some View {
        HStack(spacing: 10) {
            Circle()
                .fill(isOverdue ? Color.red : Color.orange)
                .frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(activity.subject ?? "")
                    .fontWeight(.medium)
                HStack(spacing: 6) {
                    Text(activity.activityType ?? "")
                        .font(.caption)
                    if let d = activity.dueDate {
                        Text(d, style: .relative)
                            .font(.caption)
                            .foregroundColor(isOverdue ? .red : .secondary)
                    }
                    if let c = activity.contact {
                        Text("- \(c.firstName ?? "") \(c.lastName ?? "")")
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                }
                .foregroundColor(.secondary)
            }
            Spacer()
            if isOverdue {
                Text("Vencida")
                    .font(.caption2)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(Color.red.opacity(0.15))
                    .foregroundColor(.red)
                    .cornerRadius(6)
            }
            Button("Completar") {
                activity.isCompleted = true
                activity.updatedAt = Date()
                PersistenceController.shared.save()
                intelligence.analyze(context: context)
            }
            .buttonStyle(.bordered)
            .tint(.green)
            .controlSize(.mini)
        }
        .padding(.vertical, 3)
    }

    private func alertColor(_ priority: CRMIntelligence.CRMAlert.Priority) -> Color {
        switch priority {
        case .critical: return .red
        case .high: return .orange
        case .medium: return .yellow
        case .low: return .gray
        }
    }

    private func alertsMainColor() -> Color {
        if intelligence.alerts.contains(where: { $0.priority == .critical }) { return .red }
        if intelligence.alerts.contains(where: { $0.priority == .high }) { return .orange }
        return .yellow
    }

    private func alertIcon(_ type: CRMIntelligence.CRMAlert.AlertType) -> String {
        switch type {
        case .followUp: return "FU"
        case .overdueActivity: return "AV"
        case .upcomingClose: return "OC"
        case .hotLead: return "LC"
        case .ticketOverdue: return "TK"
        case .noActivity: return "SA"
        case .staleOpportunity: return "OE"
        }
    }

    func leadStatusColor(_ status: String) -> Color {
        switch status {
        case "new": return .blue
        case "contacted": return .orange
        case "qualified": return .green
        case "lost": return .red
        default: return .gray
        }
    }

    func stageColor(_ stage: String) -> Color {
        switch stage {
        case "prospecting": return .blue
        case "qualification": return .orange
        case "proposal": return .purple
        case "negotiation": return .green
        default: return .gray
        }
    }
}

struct KPICard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(color)
            Text(subtitle)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(nsColor: .controlBackgroundColor))
        .cornerRadius(10)
        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.gray.opacity(0.2)))
    }
}

struct StatusBadge: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(.caption2)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(color.opacity(0.15))
            .foregroundColor(color)
            .cornerRadius(8)
    }
}
