import SwiftUI
import CoreData

struct ContactListView: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDContact.lastName, ascending: true)],
        animation: .default
    ) private var contacts: FetchedResults<CDContact>

    @State private var searchText = ""
    @State private var showingForm = false
    @State private var selectedContact: CDContact?

    var filteredContacts: [CDContact] {
        if searchText.isEmpty { return Array(contacts) }
        return contacts.filter {
            ($0.firstName ?? "").localizedCaseInsensitiveContains(searchText) ||
            ($0.lastName ?? "").localizedCaseInsensitiveContains(searchText) ||
            ($0.email ?? "").localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Contactos")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                TextField("Buscar...", text: $searchText)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 200)
                Button("Nuevo contacto") {
                    selectedContact = nil
                    showingForm = true
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
            .padding()

            // Table
            Table(filteredContacts) {
                TableColumn("Nombre") { contact in
                    Text("\(contact.firstName ?? "") \(contact.lastName ?? "")")
                        .fontWeight(.medium)
                }
                TableColumn("Email") { contact in
                    Text(contact.email ?? "-")
                }
                TableColumn("Telefono") { contact in
                    Text(contact.phone ?? "-")
                }
                TableColumn("Empresa") { contact in
                    Text(contact.company?.name ?? "-")
                }
                TableColumn("Estado") { contact in
                    StatusBadge(text: contact.status ?? "active", color: contactStatusColor(contact.status ?? "active"))
                }
                TableColumn("Acciones") { contact in
                    HStack(spacing: 8) {
                        Button("Editar") {
                            selectedContact = contact
                            showingForm = true
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Eliminar") {
                            deleteContact(contact)
                        }
                        .buttonStyle(.bordered)
                        .tint(.red)
                        .controlSize(.small)
                    }
                }
            }
        }
        .sheet(isPresented: $showingForm) {
            ContactFormView(contact: selectedContact)
        }
    }

    private func deleteContact(_ contact: CDContact) {
        context.delete(contact)
        PersistenceController.shared.save()
    }

    private func contactStatusColor(_ status: String) -> Color {
        switch status {
        case "active": return .green
        case "inactive": return .gray
        case "customer": return .blue
        case "prospect": return .orange
        default: return .gray
        }
    }
}

struct ContactFormView: View {
    @Environment(\.managedObjectContext) private var context
    @Environment(\.dismiss) private var dismiss

    let contact: CDContact?

    @State private var firstName = ""
    @State private var lastName = ""
    @State private var email = ""
    @State private var phone = ""
    @State private var mobile = ""
    @State private var jobTitle = ""
    @State private var city = ""
    @State private var country = ""
    @State private var status = "active"
    @State private var notes = ""

    let statusOptions = ["active", "inactive", "customer", "prospect"]

    var isEditing: Bool { contact != nil }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(isEditing ? "Editar contacto" : "Nuevo contacto")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Button("Cancelar") { dismiss() }
                    .buttonStyle(.bordered)
                Button("Guardar") { save() }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
            }
            .padding()

            Form {
                Section("Datos personales") {
                    TextField("Nombre", text: $firstName)
                    TextField("Apellido", text: $lastName)
                    TextField("Email", text: $email)
                    TextField("Telefono", text: $phone)
                    TextField("Movil", text: $mobile)
                    TextField("Cargo", text: $jobTitle)
                }
                Section("Ubicacion") {
                    TextField("Ciudad", text: $city)
                    TextField("Pais", text: $country)
                }
                Section("Estado") {
                    Picker("Estado", selection: $status) {
                        ForEach(statusOptions, id: \.self) { Text($0) }
                    }
                }
                Section("Notas") {
                    TextEditor(text: $notes)
                        .frame(height: 80)
                }
            }
            .formStyle(.grouped)
        }
        .frame(width: 500, height: 600)
        .onAppear { loadData() }
    }

    private func loadData() {
        guard let c = contact else { return }
        firstName = c.firstName ?? ""
        lastName = c.lastName ?? ""
        email = c.email ?? ""
        phone = c.phone ?? ""
        mobile = c.mobile ?? ""
        jobTitle = c.jobTitle ?? ""
        city = c.city ?? ""
        country = c.country ?? ""
        status = c.status ?? "active"
        notes = c.notes ?? ""
    }

    private func save() {
        let c = contact ?? CDContact(context: context)
        if contact == nil {
            c.id = UUID()
            c.createdAt = Date()
        }
        c.firstName = firstName
        c.lastName = lastName
        c.email = email
        c.phone = phone
        c.mobile = mobile
        c.jobTitle = jobTitle
        c.city = city
        c.country = country
        c.status = status
        c.notes = notes
        c.updatedAt = Date()
        PersistenceController.shared.save()
        dismiss()
    }
}
