import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BookingModule } from './booking/booking.module';
import { TableModule } from './table/table.module';
import { CustomerModule } from './customer/customer.module';
import { MenuModule } from './menu/menu.module';
import { OrderModule } from './order/order.module';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: 'localhost',
      port: 5433,
      username: 'postgres',
      password: 'admin',
      database: 'restaurante',
      autoLoadEntities: true,
      synchronize: true, // Solo para desarrollo, no usar en producción
    }),
    BookingModule,
    TableModule,
    CustomerModule,
    MenuModule,
    OrderModule,
  ],
})
export class AppModule {}
