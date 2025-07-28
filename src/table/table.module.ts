import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Table } from '../entities/table.entity';
import { TableService } from './table.service';
import { TableController } from './table.controller';

@Module({
  imports: [TypeOrmModule.forFeature([Table])],
  providers: [TableService],
  controllers: [TableController],
  exports: [TableService],
})
export class TableModule {}
