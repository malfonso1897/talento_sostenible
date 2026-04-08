
import SwiftUI

enum SidebarItem: String, CaseIterable, Identifiable {
    case dashboard = "Dashboard"
    case contactos = "Contactos"
    case empresas = "Empresas"
    case leads = "Leads"
    case oportunidades = "Oportunidades"
    case pipeline = "Pipeline"
    case actividades = "Actividades"
    case calendario = "Calendario"
    case campanas = "Campa\u{00f1}as"
    case tickets = "Tickets"
    case automatizacion = "Automatizacion"
    case analitica = "Analitica"

    var id: String { rawValue }
}

struct ContentView: View {
    @State private var selectedItem: SidebarItem? = .dashboard

    var body: some View {
        NavigationSplitView {
            List(SidebarItem.allCases, selection: $selectedItem) { item in
                Text(item.rawValue)
                    .tag(item)
            }
            .listStyle(.sidebar)
            .navigationTitle("TALENTO SOSTENIBLE")
            .frame(minWidth: 200)
        } detail: {
            switch selectedItem {
            case .dashboard:
                DashboardView()
            case .contactos:
                ContactListView()
            case .empresas:
                CompanyListView()
            case .leads:
                LeadListView()
            case .oportunidades:
                OpportunityListView()
            case .pipeline:
                PipelineView()
            case .actividades:
                ActivityListView()
            case .calendario:
                CalendarView()
            case .campanas:
                CampaignListView()
            case .tickets:
                TicketListView()
            case .automatizacion:
                WorkflowListView()
            case .analitica:
                AnalyticsView()
            case .none:
                Text("Selecciona una seccion")
                    .foregroundColor(.secondary)
            }
        }
    }
}
