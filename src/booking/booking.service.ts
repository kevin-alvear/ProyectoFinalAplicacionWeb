import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Booking } from '../entities/booking.entity';
import { Repository } from 'typeorm';
import { CreateBookingDto } from './dto/create-booking.dto';
import { Table } from '../entities/table.entity';

@Injectable()
export class BookingService {
  constructor(
    @InjectRepository(Booking)
    private bookingRepo: Repository<Booking>,
    @InjectRepository(Table)
    private tableRepo: Repository<Table>,
  ) {}

  async create(dto: CreateBookingDto): Promise<Booking> {
    const booking = new Booking();
    booking.name = dto.name;
    booking.phoneNumber = dto.phoneNumber;
    booking.peopleQty = dto.peopleQty;
    booking.date = new Date(dto.date);
    booking.confirmed = dto.confirmed;

    const tables = await this.tableRepo.findByIds(dto.tables);
    booking.tables = tables;

    return this.bookingRepo.save(booking);
  }

  async findByPhone(phone: string): Promise<Booking[]> {
    return this.bookingRepo.find({
      where: { phoneNumber: phone },
      relations: ['tables'],
    });
  }

  async remove(id: number): Promise<void> {
    await this.bookingRepo.delete(id);
  }
}
