import SwiftUI
import CoreData

struct ActivityListView: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDActivity.dueDate, ascending: false)],
        animation: .default
    ) private var activities: FetchedResults<CDActivity>

    @State private var searchText = ""
    @State private var showingForm = false
    @State private var selectedActivity: CDActivity?

    var filteredActivities: [CDActivity] {
        if searchText.isEmpty { return Array(activities) }
        return activities.filter {
            ($0.subject ?? "").localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Actividades")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                TextField("Buscar...", text: $searchText)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 200)
                Button("Nueva actividad") {
                    selectedActivity = nil
                    showingForm = true
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
            .padding()

            Table(filteredActivities) {
                TableColumn("Asunto") { activity in
                    Text(activity.subject ?? "")
                        .fontWeight(.medium)
                }
                TableColumn("Tipo") { activity in
                    Text(activity.activityType ?? "tarea")
                }
                TableColumn("Fecha") { activity in
                    if let date = activity.dueDate {
                        Text(date, style: .date)
                    } else {
                        Text("-")
                    }
                }
                TableColumn("Contacto") { activity in
                    if let c = activity.contact {
                        Text("\(c.firstName ?? "") \(c.lastName ?? "")")
                    } else {
                        Text("-")
                    }
                }
                TableColumn("Estado") { activity in
                    if activity.isCompleted {
                        StatusBadge(text: "Completada", color: .green)
                    } else {
                        StatusBadge(text: "Pendiente", color: .orange)
                    }
                }
                TableColumn("Acciones") { activity in
                    HStack(spacing: 6) {
                        if !activity.isCompleted {
                            Button("Completar") {
                                activity.isCompleted = true
                                activity.updatedAt = Date()
                                PersistenceController.shared.save()
                            }
                            .buttonStyle(.bordered)
                            .tint(.green)
                            .controlSize(.small)
                        }
                        Button("Editar") {
                            selectedActivity = activity
                            showingForm = true
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Eliminar") {
                            context.delete(activity)
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
            ActivityFormView(activity: selectedActivity)
        }
    }
}

struct ActivityFormView: View {
    @Environment(\.managedObjectContext) private var context
    @Environment(\.dismiss) private var dismiss
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \CDContact.lastName, ascending: true)]) private var contacts: FetchedResults<CDContact>
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \CDCompany.name, ascending: true)]) private var companies: FetchedResults<CDCompany>

    let activity: CDActivity?

    @State private var subject = ""
    @State private var activityType = "task"
    @State private var dueDate = Date()
    @State private var duration: Int32 = 30
    @State private var priority = "medium"
    @State private var notes = ""
    @State private var selectedContact: CDContact?
    @State private var selectedCompany: CDCompany?

    let typeOptions = ["task", "call", "email", "meeting", "visit"]
    let priorityOptions = ["low", "medium", "high", "urgent"]

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(activity != nil ? "Editar actividad" : "Nueva actividad")
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
                    Picker("Tipo", selection: $activityType) {
                        ForEach(typeOptions, id: \.self) { Text($0) }
                    }
                    DatePicker("Fecha", selection: $dueDate)
                    Stepper("Duracion: \(duration) min", value: $duration, in: 5...480, step: 15)
                    Picker("Prioridad", selection: $priority) {
                        ForEach(priorityOptions, id: \.self) { Text($0) }
                    }
                }
                Section("Relaciones") {
                    Picker("Contacto", selection: $selectedContact) {
                        Text("Ninguno").tag(nil as CDContact?)
                        ForEach(contacts) { c in
                            Text("\(c.firstName ?? "") \(c.lastName ?? "")").tag(c as CDContact?)
                        }
                    }
                    Picker("Empresa", selection: $selectedCompany) {
                        Text("Ninguna").tag(nil as CDCompany?)
                        ForEach(companies) { c in
                            Text(c.name ?? "").tag(c as CDCompany?)
                        }
                    }
                }
                Section("Notas") {
                    TextEditor(text: $notes)
                        .frame(height: 80)
                }
            }
            .formStyle(.grouped)
        }
        .frame(width: 500, height: 550)
        .onAppear {
            guard let a = activity else { return }
            subject = a.subject ?? ""
            activityType = a.activityType ?? "task"
            dueDate = a.dueDate ?? Date()
            duration = a.duration
            priority = a.priority ?? "medium"
            notes = a.notes ?? ""
            selectedContact = a.contact
            selectedCompany = a.company
        }
    }

    private func save() {
        let a = activity ?? CDActivity(context: context)
        if activity == nil {
            a.id = UUID()
            a.createdAt = Date()
            a.isCompleted = false
        }
        a.subject = subject
        a.activityType = activityType
        a.dueDate = dueDate
        a.duration = duration
        a.priority = priority
        a.notes = notes
        a.contact = selectedContact
        a.company = selectedCompany
        a.updatedAt = Date()
        PersistenceController.shared.save()
        // Programar notificacion 15 min antes
        NotificationManager.shared.scheduleActivityReminder(a)
        dismiss()
    }
}

import EventKit

// MARK: - Calendario nativo integrado

class CalendarManager: ObservableObject {
    let store = EKEventStore()
    @Published var authorized = false
    @Published var macEvents: [EKEvent] = []

    func requestAccess() {
        if #available(macOS 14.0, *) {
            store.requestFullAccessToEvents { granted, _ in
                DispatchQueue.main.async { self.authorized = granted }
            }
        } else {
            store.requestAccess(to: .event) { granted, _ in
                DispatchQueue.main.async { self.authorized = granted }
            }
        }
    }

    func fetchEvents(for date: Date) {
        guard authorized else { return }
        let cal = Foundation.Calendar.current
        let start = cal.startOfDay(for: date)
        guard let end = cal.date(byAdding: .day, value: 1, to: start) else { return }
        let predicate = store.predicateForEvents(withStart: start, end: end, calendars: nil)
        let events = store.events(matching: predicate)
        DispatchQueue.main.async { self.macEvents = events }
    }

    func addEvent(title: String, startDate: Date, endDate: Date, notes: String?) {
        guard authorized else { return }
        let event = EKEvent(eventStore: store)
        event.title = title
        event.startDate = startDate
        event.endDate = endDate
        event.notes = notes
        event.calendar = store.defaultCalendarForNewEvents
        try? store.save(event, span: .thisEvent)
    }

    func removeEvent(_ event: EKEvent) {
        try? store.remove(event, span: .thisEvent)
    }
}

struct CalendarView: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDActivity.dueDate, ascending: true)],
        predicate: NSPredicate(format: "isCompleted == NO")
    ) private var activities: FetchedResults<CDActivity>

    @State private var selectedDate = Date()
    @State private var displayedMonth = Date()
    @State private var showingForm = false
    @State private var showingEventForm = false
    @StateObject private var calendarManager = CalendarManager()

    private let cal = Foundation.Calendar.current
    private let weekdays = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

    private var activitiesForDate: [CDActivity] {
        activities.filter { activity in
            guard let date = activity.dueDate else { return false }
            return cal.isDate(date, inSameDayAs: selectedDate)
        }
    }

    // Genera las filas de dias del mes para la cuadricula
    private var monthDays: [[Date?]] {
        let comps = cal.dateComponents([.year, .month], from: displayedMonth)
        guard let firstOfMonth = cal.date(from: comps),
              let range = cal.range(of: .day, in: .month, for: firstOfMonth) else { return [] }

        // Dia de la semana del 1ro (lunes=1)
        var weekday = cal.component(.weekday, from: firstOfMonth)
        // Convertir de domingo=1 a lunes=1
        weekday = weekday == 1 ? 7 : weekday - 1

        var days: [Date?] = Array(repeating: nil, count: weekday - 1)
        for day in range {
            if let date = cal.date(byAdding: .day, value: day - 1, to: firstOfMonth) {
                days.append(date)
            }
        }
        // Rellenar hasta completar la ultima fila
        while days.count % 7 != 0 { days.append(nil) }

        return stride(from: 0, to: days.count, by: 7).map { Array(days[$0..<min($0+7, days.count)]) }
    }

    private var monthTitle: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "es_ES")
        formatter.dateFormat = "MMMM yyyy"
        return formatter.string(from: displayedMonth).capitalized
    }

    private func activityCount(for date: Date) -> Int {
        activities.filter { a in
            guard let d = a.dueDate else { return false }
            return cal.isDate(d, inSameDayAs: date)
        }.count
    }

    private func macEventCount(for date: Date) -> Int {
        guard calendarManager.authorized else { return 0 }
        let start = cal.startOfDay(for: date)
        guard let end = cal.date(byAdding: .day, value: 1, to: start) else { return 0 }
        let pred = calendarManager.store.predicateForEvents(withStart: start, end: end, calendars: nil)
        return calendarManager.store.events(matching: pred).count
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Calendario")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                if calendarManager.authorized {
                    Button("Nuevo evento Mac") {
                        showingEventForm = true
                    }
                    .buttonStyle(.bordered)
                    .tint(.blue)
                }
                Button("Nueva actividad CRM") {
                    showingForm = true
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
            .padding()

            HStack(alignment: .top, spacing: 0) {
                // MARK: - Cuadricula de mes estilo Calendario Mac
                VStack(spacing: 0) {
                    // Navegacion de mes
                    HStack {
                        Button(action: { changeMonth(-1) }) {
                            Text("<")
                                .font(.title2)
                                .fontWeight(.semibold)
                                .frame(width: 36, height: 36)
                        }
                        .buttonStyle(.plain)

                        Spacer()
                        Text(monthTitle)
                            .font(.title2)
                            .fontWeight(.semibold)
                        Spacer()

                        Button("Hoy") {
                            displayedMonth = Date()
                            selectedDate = Date()
                            calendarManager.fetchEvents(for: selectedDate)
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)

                        Button(action: { changeMonth(1) }) {
                            Text(">")
                                .font(.title2)
                                .fontWeight(.semibold)
                                .frame(width: 36, height: 36)
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.horizontal, 12)
                    .padding(.bottom, 8)

                    // Dias de la semana
                    HStack(spacing: 0) {
                        ForEach(weekdays, id: \.self) { day in
                            Text(day)
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .padding(.horizontal, 4)
                    .padding(.bottom, 4)

                    Divider()

                    // Cuadricula de dias
                    VStack(spacing: 0) {
                        ForEach(monthDays.indices, id: \.self) { rowIndex in
                            HStack(spacing: 0) {
                                ForEach(0..<7, id: \.self) { colIndex in
                                    if let date = monthDays[rowIndex][colIndex] {
                                        dayCell(date: date)
                                    } else {
                                        Color.clear.frame(maxWidth: .infinity, minHeight: 70)
                                    }
                                }
                            }
                            if rowIndex < monthDays.count - 1 {
                                Divider()
                            }
                        }
                    }
                    .padding(.horizontal, 4)
                }
                .frame(minWidth: 500)

                Divider()

                // MARK: - Panel lateral derecho
                VStack(alignment: .leading, spacing: 12) {
                    let dayFormatter: DateFormatter = {
                        let f = DateFormatter()
                        f.locale = Locale(identifier: "es_ES")
                        f.dateFormat = "EEEE d 'de' MMMM"
                        return f
                    }()

                    Text(dayFormatter.string(from: selectedDate).capitalized)
                        .font(.title3)
                        .fontWeight(.bold)
                        .padding(.bottom, 4)

                    ScrollView {
                        VStack(alignment: .leading, spacing: 12) {
                            // Actividades CRM del dia
                            if !activitiesForDate.isEmpty {
                                Text("Actividades CRM")
                                    .font(.headline)
                                    .foregroundColor(.green)
                                ForEach(activitiesForDate) { activity in
                                    HStack(spacing: 8) {
                                        RoundedRectangle(cornerRadius: 2)
                                            .fill(Color.green)
                                            .frame(width: 4)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(activity.subject ?? "")
                                                .fontWeight(.medium)
                                                .lineLimit(1)
                                            HStack(spacing: 6) {
                                                Text(activity.activityType ?? "")
                                                    .font(.caption)
                                                if let d = activity.dueDate {
                                                    Text(d, style: .time)
                                                        .font(.caption)
                                                }
                                                Text("\(activity.duration) min")
                                                    .font(.caption)
                                            }
                                            .foregroundColor(.secondary)
                                            if let c = activity.contact {
                                                Text("\(c.firstName ?? "") \(c.lastName ?? "")")
                                                    .font(.caption)
                                                    .foregroundColor(.green)
                                            }
                                        }
                                        Spacer()
                                        Button("Completar") {
                                            activity.isCompleted = true
                                            activity.updatedAt = Date()
                                            PersistenceController.shared.save()
                                        }
                                        .buttonStyle(.bordered)
                                        .tint(.green)
                                        .controlSize(.mini)
                                    }
                                    .padding(8)
                                    .background(Color.green.opacity(0.06))
                                    .cornerRadius(6)
                                }
                            }

                            // Eventos Mac del dia
                            if calendarManager.authorized {
                                if !calendarManager.macEvents.isEmpty {
                                    Text("Eventos Mac")
                                        .font(.headline)
                                        .foregroundColor(.blue)
                                        .padding(.top, activitiesForDate.isEmpty ? 0 : 8)
                                    ForEach(calendarManager.macEvents, id: \.eventIdentifier) { event in
                                        HStack(spacing: 8) {
                                            RoundedRectangle(cornerRadius: 2)
                                                .fill(Color(cgColor: event.calendar.cgColor))
                                                .frame(width: 4)
                                            VStack(alignment: .leading, spacing: 2) {
                                                Text(event.title ?? "")
                                                    .fontWeight(.medium)
                                                    .lineLimit(1)
                                                HStack(spacing: 6) {
                                                    if event.isAllDay {
                                                        Text("Todo el dia")
                                                            .font(.caption)
                                                    } else {
                                                        if let s = event.startDate {
                                                            Text(s, style: .time).font(.caption)
                                                        }
                                                        Text("-").font(.caption)
                                                        if let e = event.endDate {
                                                            Text(e, style: .time).font(.caption)
                                                        }
                                                    }
                                                    Text(event.calendar.title)
                                                        .font(.caption)
                                                        .foregroundColor(.secondary)
                                                }
                                                .foregroundColor(.secondary)
                                            }
                                            Spacer()
                                        }
                                        .padding(8)
                                        .background(Color(cgColor: event.calendar.cgColor).opacity(0.08))
                                        .cornerRadius(6)
                                    }
                                }
                            } else {
                                VStack(spacing: 8) {
                                    Text("Conecta tu calendario Mac")
                                        .foregroundColor(.secondary)
                                    Button("Autorizar acceso") {
                                        calendarManager.requestAccess()
                                    }
                                    .buttonStyle(.borderedProminent)
                                    .tint(.blue)
                                    .controlSize(.small)
                                }
                                .padding(.top, 12)
                            }

                            // Sin eventos ni actividades
                            if activitiesForDate.isEmpty && (calendarManager.macEvents.isEmpty || !calendarManager.authorized) {
                                Text("Sin eventos para este dia")
                                    .foregroundColor(.secondary)
                                    .padding(.top, 20)
                            }
                        }
                    }
                    Spacer()
                }
                .frame(width: 300)
                .padding()
            }
        }
        .sheet(isPresented: $showingForm) {
            ActivityFormView(activity: nil)
        }
        .sheet(isPresented: $showingEventForm) {
            MacEventFormView(calendarManager: calendarManager, selectedDate: selectedDate) {
                calendarManager.fetchEvents(for: selectedDate)
            }
        }
        .onAppear {
            calendarManager.requestAccess()
            calendarManager.fetchEvents(for: selectedDate)
        }
    }

    // Celda de cada dia en la cuadricula
    @ViewBuilder
    private func dayCell(date: Date) -> some View {
        let isToday = cal.isDateInToday(date)
        let isSelected = cal.isDate(date, inSameDayAs: selectedDate)
        let crmCount = activityCount(for: date)
        let macCount = macEventCount(for: date)
        let dayNum = cal.component(.day, from: date)

        VStack(spacing: 2) {
            // Numero del dia
            ZStack {
                if isToday {
                    Circle()
                        .fill(Color.red)
                        .frame(width: 24, height: 24)
                }
                Text("\(dayNum)")
                    .font(.system(size: 13, weight: isToday ? .bold : .regular))
                    .foregroundColor(isToday ? .white : .primary)
            }
            .padding(.top, 4)

            // Indicadores de eventos
            if crmCount > 0 || macCount > 0 {
                HStack(spacing: 3) {
                    if crmCount > 0 {
                        Circle().fill(Color.green).frame(width: 6, height: 6)
                    }
                    if macCount > 0 {
                        Circle().fill(Color.blue).frame(width: 6, height: 6)
                    }
                }
                if crmCount + macCount > 0 {
                    Text("\(crmCount + macCount)")
                        .font(.system(size: 9))
                        .foregroundColor(.secondary)
                }
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, minHeight: 70)
        .background(
            isSelected
                ? Color.accentColor.opacity(0.12)
                : Color.clear
        )
        .cornerRadius(4)
        .contentShape(Rectangle())
        .onTapGesture {
            selectedDate = date
            calendarManager.fetchEvents(for: date)
        }
    }

    private func changeMonth(_ offset: Int) {
        if let newMonth = cal.date(byAdding: .month, value: offset, to: displayedMonth) {
            displayedMonth = newMonth
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
}

// Formulario para crear eventos en el calendario nativo de Mac
struct MacEventFormView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var calendarManager: CalendarManager
    let selectedDate: Date
    var onSave: () -> Void

    @State private var title = ""
    @State private var startTime = Date()
    @State private var endTime = Date()
    @State private var notes = ""

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Nuevo evento - Calendario Mac")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Button("Cancelar") { dismiss() }
                    .buttonStyle(.bordered)
                Button("Crear evento") { save() }
                    .buttonStyle(.borderedProminent)
                    .tint(.blue)
                    .disabled(title.isEmpty)
            }
            .padding()

            Form {
                Section("Datos del evento") {
                    TextField("Titulo", text: $title)
                    DatePicker("Inicio", selection: $startTime)
                    DatePicker("Fin", selection: $endTime)
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
            let cal = Foundation.Calendar.current
            startTime = cal.date(bySettingHour: 9, minute: 0, second: 0, of: selectedDate) ?? selectedDate
            endTime = cal.date(bySettingHour: 10, minute: 0, second: 0, of: selectedDate) ?? selectedDate
        }
    }

    private func save() {
        calendarManager.addEvent(
            title: title,
            startDate: startTime,
            endDate: endTime,
            notes: notes.isEmpty ? nil : notes
        )
        onSave()
        dismiss()
    }
}
