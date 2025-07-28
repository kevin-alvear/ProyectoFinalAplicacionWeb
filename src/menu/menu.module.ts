import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm'; // Importa TypeOrmModule
import { MenuService } from './menu.service';
import { MenuController } from './menu.controller';
import { Menu } from '../entities/menu.entity'; // Importa tu entidad Menu

@Module({
  imports: [
    TypeOrmModule.forFeature([Menu]) 
  ],
  controllers: [MenuController],
  providers: [MenuService],
  exports: [MenuService], 
})
export class MenuModule {}
