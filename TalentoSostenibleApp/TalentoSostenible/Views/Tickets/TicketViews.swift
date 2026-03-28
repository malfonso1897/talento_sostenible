import SwiftUI
import CoreData

struct TicketListView: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDTicket.createdAt, ascending: false)],
        animation: .default
    ) private var tickets: FetchedResults<CDTicket>

    @State private var showingForm = false
    @State private var selectedTicket: CDTicket?
    @State private var showingDetail = false

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Tickets")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                Button("Nuevo ticket") {
                    selectedTicket = nil
                    showingForm = true
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
            .padding()

            Table(tickets) {
                TableColumn("Asunto") { t in
                    Text(t.subject ?? "").fontWeight(.medium)
                }
                TableColumn("Contacto") { t in
                    if let c = t.contact {
                        Text("\(c.firstName ?? "") \(c.lastName ?? "")")
                    } else {
                        Text("-")
                    }
                }
                TableColumn("Prioridad") { t in
                    StatusBadge(text: t.priority ?? "medium", color: priorityColor(t.priority ?? "medium"))
                }
                TableColumn("Estado") { t in
                    StatusBadge(text: ticketStatusLabel(t.status ?? "open"), color: ticketStatusColor(t.status ?? "open"))
                }
                TableColumn("Fecha") { t in
                    if let d = t.createdAt { Text(d, style: .date) } else { Text("-") }
                }
                TableColumn("Acciones") { t in
                    HStack(spacing: 6) {
                        Button("Ver") {
                            selectedTicket = t
                            showingDetail = true
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Editar") {
                            selectedTicket = t
                            showingForm = true
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Eliminar") {
                            context.delete(t)
                            PersistenceController.shared.save()
                        }
                        .buttonStyle(.bordered)
                        .tint(.red)
                        .controlSize(.small)
                    }
                }
            }
        }
        .sheet(isPresented: $showingForm) {
            TicketFormView(ticket: selectedTicket)
        }
        .sheet(isPresented: $showingDetail) {
            if let ticket = selectedTicket {
                TicketDetailView(ticket: ticket)
            }
        }
    }

    func priorityColor(_ p: String) -> Color {
        switch p {
        case "urgent": return .red
        case "high": return .orange
        case "medium": return .yellow
        case "low": return .gray
        default: return .gray
        }
    }

    func ticketStatusLabel(_ s: String) -> String {
        switch s {
        case "open": return "Abierto"
        case "in_progress": return "En curso"
        case "resolved": return "Resuelto"
        case "closed": return "Cerrado"
        default: return s
        }
    }

    func ticketStatusColor(_ s: String) -> Color {
        switch s {
        case "open": return .blue
        case "in_progress": return .orange
        case "resolved": return .green
        case "closed": return .gray
        default: return .gray
        }
    }
}

struct TicketFormView: View {
    @Environment(\.managedObjectContext) private var context
    @Environment(\.dismiss) private var dismiss
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \CDContact.lastName, ascending: true)]) private var contacts: FetchedResults<CDContact>

    let ticket: CDTicket?

    @State private var subject = ""
    @State private var ticketDescription = ""
    @State private var priority = "medium"
    @State private var status = "open"
    @State private var category = ""
    @State private var selectedContact: CDContact?

    let priorityOptions = ["low", "medium", "high", "urgent"]
    let statusOptions = ["open", "in_progress", "resolved", "closed"]

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(ticket != nil ? "Editar ticket" : "Nuevo ticket")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Button("Cancelar") { dismiss() }
                    .buttonStyle(.bordered)
                Button("Guardar") { save() }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                    .disabled(subject.isEmpty)
            }
            .padding()

            Form {
                Section("Datos") {
                    TextField("Asunto", text: $subject)
                    TextField("Categoria", text: $category)
                    Picker("Prioridad", selection: $priority) {
                        ForEach(priorityOptions, id: \.self) { Text($0) }
                    }
                    Picker("Estado", selection: $status) {
                        ForEach(statusOptions, id: \.self) { Text($0) }
                    }
                    Picker("Contacto", selection: $selectedContact) {
                        Text("Ninguno").tag(nil as CDContact?)
                        ForEach(contacts) { c in
                            Text("\(c.firstName ?? "") \(c.lastName ?? "")").tag(c as CDContact?)
                        }
                    }
                }
                Section("Descripcion") {
                    TextEditor(text: $ticketDescription)
                        .frame(height: 120)
                }
            }
            .formStyle(.grouped)
        }
        .frame(width: 500, height: 500)
        .onAppear {
            guard let t = ticket else { return }
            subject = t.subject ?? ""
            ticketDescription = t.ticketDescription ?? ""
            priority = t.priority ?? "medium"
            status = t.status ?? "open"
            category = t.category ?? ""
            selectedContact = t.contact
        }
    }

    private func save() {
        let t = ticket ?? CDTicket(context: context)
        if ticket == nil {
            t.id = UUID()
            t.createdAt = Date()
        }
        t.subject = subject
        t.ticketDescription = ticketDescription
        t.priority = priority
        t.status = status
        t.category = category
        t.contact = selectedContact
        t.updatedAt = Date()
        PersistenceController.shared.save()
        dismiss()
    }
}

struct TicketDetailView: View {
    @Environment(\.managedObjectContext) private var context
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var ticket: CDTicket
    @State private var newComment = ""

    var comments: [CDTicketComment] {
        let set = ticket.comments as? Set<CDTicketComment> ?? []
        return set.sorted { ($0.createdAt ?? Date()) < ($1.createdAt ?? Date()) }
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(ticket.subject ?? "Ticket")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Button("Cerrar") { dismiss() }
                    .buttonStyle(.bordered)
            }
            .padding()

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Info
                    GroupBox("Informacion") {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Prioridad:")
                                    .foregroundColor(.secondary)
                                Text(ticket.priority ?? "-")
                            }
                            HStack {
                                Text("Estado:")
                                    .foregroundColor(.secondary)
                                Text(ticket.status ?? "-")
                            }
                            if let desc = ticket.ticketDescription, !desc.isEmpty {
                                Text("Descripcion:")
                                    .foregroundColor(.secondary)
                                Text(desc)
                            }
                        }
                        .font(.callout)
                    }

                    // Comentarios
                    GroupBox("Comentarios") {
                        if comments.isEmpty {
                            Text("Sin comentarios")
                                .foregroundColor(.secondary)
                        } else {
                            ForEach(comments) { comment in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(comment.content ?? "")
                                    if let d = comment.createdAt {
                                        Text(d, style: .date)
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .padding(8)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color(nsColor: .controlBackgroundColor))
                                .cornerRadius(6)
                            }
                        }

                        HStack {
                            TextField("Escribir comentario...", text: $newComment)
                                .textFieldStyle(.roundedBorder)
                            Button("Enviar") { addComment() }
                                .buttonStyle(.borderedProminent)
                                .tint(.green)
                                .disabled(newComment.isEmpty)
                        }
                        .padding(.top, 8)
                    }
                }
                .padding()
            }
        }
        .frame(width: 600, height: 500)
    }

    private func addComment() {
        let comment = CDTicketComment(context: context)
        comment.id = UUID()
        comment.content = newComment
        comment.createdAt = Date()
        comment.ticket = ticket
        newComment = ""
        PersistenceController.shared.save()
    }
}
