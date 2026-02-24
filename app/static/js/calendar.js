// Calendar component for date and time selection

class Calendar {
    constructor(containerId, serviceId) {
        this.container = document.getElementById(containerId);
        this.serviceId = serviceId;
        this.currentDate = new Date();
        this.selectedDate = null;
        this.selectedTimeSlot = null;
        
        this.init();
    }
    
    init() {
        this.render();
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.render();
        });
        
        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.render();
        });
    }
    
    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Update month display
        const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                           'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
        document.getElementById('currentMonth').textContent = `${monthNames[month]} ${year}`;
        
        // Clear calendar
        this.container.innerHTML = '';
        
        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Add day headers
        const dayHeaders = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        dayHeaders.forEach(day => {
            const header = document.createElement('div');
            header.style.fontWeight = 'bold';
            header.style.textAlign = 'center';
            header.style.padding = '10px';
            header.textContent = day;
            this.container.appendChild(header);
        });
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            this.container.appendChild(emptyCell);
        }
        
        // Add day cells
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-day';
            dayCell.textContent = day;
            
            // Disable past dates
            if (date < today) {
                dayCell.classList.add('disabled');
            } else {
                dayCell.addEventListener('click', () => this.selectDate(date));
            }
            
            this.container.appendChild(dayCell);
        }
    }
    
    async selectDate(date) {
        this.selectedDate = date;
        
        // Update selected state
        document.querySelectorAll('.calendar-day').forEach(cell => {
            cell.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Format date for display
        const dateStr = date.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
        document.getElementById('selectedDateDisplay').textContent = dateStr;
        
        // Store date in hidden input
        const isoDate = date.toISOString().split('T')[0];
        document.getElementById('selectedDate').value = isoDate;
        
        // Fetch available time slots
        await this.fetchTimeSlots(isoDate);
        
        // Show time slots container
        document.getElementById('timeSlotsContainer').classList.remove('hidden');
        
        // Hide form until time slot is selected
        document.getElementById('bookingFormContainer').classList.add('hidden');
    }
    
    async fetchTimeSlots(date) {
        try {
            const response = await fetch(`/api/slots?date=${date}`);
            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            this.renderTimeSlots(data.slots);
        } catch (error) {
            console.error('Error fetching time slots:', error);
            alert('Ошибка загрузки доступного времени');
        }
    }
    
    renderTimeSlots(slots) {
        const container = document.getElementById('timeSlots');
        container.innerHTML = '';
        
        slots.forEach(slot => {
            const slotEl = document.createElement('div');
            slotEl.className = 'time-slot';
            slotEl.textContent = slot.time;
            
            if (!slot.available) {
                slotEl.classList.add('unavailable');
                slotEl.title = 'Время занято';
            } else {
                slotEl.addEventListener('click', () => this.selectTimeSlot(slot.time, slotEl));
            }
            
            container.appendChild(slotEl);
        });
    }
    
    selectTimeSlot(timeSlot, element) {
        this.selectedTimeSlot = timeSlot;
        
        // Update selected state
        document.querySelectorAll('.time-slot').forEach(slot => {
            slot.classList.remove('selected');
        });
        element.classList.add('selected');
        
        // Store time slot in hidden input
        document.getElementById('selectedTimeSlot').value = timeSlot;
        
        // Show booking form
        document.getElementById('bookingFormContainer').classList.remove('hidden');
        
        // Scroll to form
        document.getElementById('bookingFormContainer').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}
