import SwiftUI
import CoreData

struct WorkflowListView: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDWorkflow.createdAt, ascending: false)],
        animation: .default
    ) private var workflows: FetchedResults<CDWorkflow>

    @State private var showingForm = false
    @State private var selectedWorkflow: CDWorkflow?

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Automatizacion")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                Button("Nuevo workflow") {
                    selectedWorkflow = nil
                    showingForm = true
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
            .padding()

            Table(workflows) {
                TableColumn("Nombre") { w in
                    Text(w.name ?? "").fontWeight(.medium)
                }
                TableColumn("Disparador") { w in
                    Text(w.triggerType ?? "-")
                }
                TableColumn("Accion") { w in
                    Text(w.actionType ?? "-")
                }
                TableColumn("Estado") { w in
                    if w.isActive {
                        StatusBadge(text: "Activo", color: .green)
                    } else {
                        StatusBadge(text: "Inactivo", color: .gray)
                    }
                }
                TableColumn("Ejecuciones") { w in
                    Text("\(w.executionCount)")
                }
                TableColumn("Acciones") { w in
                    HStack(spacing: 6) {
                        Button(w.isActive ? "Desactivar" : "Activar") {
                            w.isActive.toggle()
                            w.updatedAt = Date()
                            PersistenceController.shared.save()
                        }
                        .buttonStyle(.bordered)
                        .tint(w.isActive ? .orange : .green)
                        .controlSize(.small)
                        Button("Editar") {
                            selectedWorkflow = w
                            showingForm = true
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Eliminar") {
                            context.delete(w)
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
            WorkflowFormView(workflow: selectedWorkflow)
        }
    }
}

struct WorkflowFormView: View {
    @Environment(\.managedObjectContext) private var context
    @Environment(\.dismiss) private var dismiss

    let workflow: CDWorkflow?

    @State private var name = ""
    @State private var triggerType = "manual"
    @State private var actionType = "notification"
    @State private var isActive = true
    @State private var notes = ""

    let triggerOptions = ["manual", "nuevo_lead", "cambio_etapa", "ticket_creado", "fecha_programada"]
    let actionOptions = ["notification", "email", "crear_tarea", "cambiar_estado", "asignar"]

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(workflow != nil ? "Editar workflow" : "Nuevo workflow")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Button("Cancelar") { dismiss() }
                    .buttonStyle(.bordered)
                Button("Guardar") { save() }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                    .disabled(name.isEmpty)
            }
            .padding()

            Form {
                Section("Datos") {
                    TextField("Nombre", text: $name)
                    Picker("Disparador", selection: $triggerType) {
                        ForEach(triggerOptions, id: \.self) { Text($0) }
                    }
                    Picker("Accion", selection: $actionType) {
                        ForEach(actionOptions, id: \.self) { Text($0) }
                    }
                    Toggle("Activo", isOn: $isActive)
                }
                Section("Notas") {
                    TextEditor(text: $notes)
                        .frame(height: 80)
                }
            }
            .formStyle(.grouped)
        }
        .frame(width: 450, height: 400)
        .onAppear {
            guard let w = workflow else { return }
            name = w.name ?? ""
            triggerType = w.triggerType ?? "manual"
            actionType = w.actionType ?? "notification"
            isActive = w.isActive
            notes = w.notes ?? ""
        }
    }

    private func save() {
        let w = workflow ?? CDWorkflow(context: context)
        if workflow == nil {
            w.id = UUID()
            w.createdAt = Date()
            w.executionCount = 0
        }
        w.name = name
        w.triggerType = triggerType
        w.actionType = actionType
        w.isActive = isActive
        w.notes = notes
        w.updatedAt = Date()
        PersistenceController.shared.save()
        dismiss()
    }
}
