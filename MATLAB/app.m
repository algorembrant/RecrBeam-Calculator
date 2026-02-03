classdef BeamAnalysisApp < matlab.apps.AppBase
    % BeamAnalysisApp - Interactive Analysis of Nominal Moment Strength (Mn)
    % Based on Example 4-1 and 4-1M from ACI 318 Provisions
    %
    % Variables from Example:
    %   fc' - Concrete compressive strength
    %   fy  - Steel yield strength
    %   Es  - Modulus of elasticity of steel
    %   b   - Beam width
    %   h   - Total beam depth
    %   d   - Effective depth (to centroid of tension steel)
    %   As  - Total area of tension steel
    %   beta1 - Stress block factor (0.85 for fc' <= 4000 psi)
    %   epsilon_cu - Ultimate concrete strain (0.003)
    %
    % Calculated:
    %   T       - Tension force in steel
    %   a       - Depth of equivalent stress block
    %   c       - Neutral axis depth
    %   epsilon_y - Yield strain of steel
    %   epsilon_s - Strain in steel at ultimate
    %   Mn      - Nominal moment strength
    %   As_min  - Minimum steel area per ACI

    properties (Access = public)
        UIFigure      matlab.ui.Figure
        MainGrid      matlab.ui.container.GridLayout
        
        % Panels
        InputPanel    matlab.ui.container.Panel
        DiagramPanel  matlab.ui.container.Panel
        ResultsPanel  matlab.ui.container.Panel
        EquationsPanel matlab.ui.container.Panel
        
        % Inputs - Material
        UnitSwitch    matlab.ui.control.Switch
        EditFc        matlab.ui.control.NumericEditField
        EditFy        matlab.ui.control.NumericEditField
        EditEs        matlab.ui.control.NumericEditField
        EditBeta1     matlab.ui.control.NumericEditField
        EditEpsCu     matlab.ui.control.NumericEditField
        
        % Inputs - Geometry
        EditB         matlab.ui.control.NumericEditField
        EditH         matlab.ui.control.NumericEditField
        EditD         matlab.ui.control.NumericEditField
        
        % Inputs - Reinforcement
        EditBars      matlab.ui.control.NumericEditField
        EditBarArea   matlab.ui.control.NumericEditField
        
        % Visualization Axes
        AxSection     matlab.ui.control.UIAxes
        AxStrain      matlab.ui.control.UIAxes
        AxStress      matlab.ui.control.UIAxes
        AxEquations   matlab.ui.control.UIAxes
        
        % Results
        ResultsText   matlab.ui.control.TextArea
    end

    properties (Access = private)
        Units struct
        % Color scheme
        Colors struct
    end

    methods (Access = private)

        function updateApp(app, ~)
            % === 1. GET INPUTS ===
            is_imperial = strcmp(app.UnitSwitch.Value, 'Imperial');
            
            fc = app.EditFc.Value;
            fy = app.EditFy.Value;
            Es = app.EditEs.Value;
            beta1 = app.EditBeta1.Value;
            epsilon_cu = app.EditEpsCu.Value;
            b  = app.EditB.Value;
            h  = app.EditH.Value;
            d  = app.EditD.Value;
            n_bars = app.EditBars.Value;
            bar_A  = app.EditBarArea.Value;
            As = n_bars * bar_A;

            % Set units
            if is_imperial
                app.Units = struct('len', 'in', 'area', 'in2', 'force', 'lb', ...
                    'stress', 'psi', 'moment', 'lb-in', 'moment_k', 'k-in', 'moment_alt', 'k-ft');
            else
                app.Units = struct('len', 'mm', 'area', 'mm2', 'force', 'N', ...
                    'stress', 'MPa', 'moment', 'N-mm', 'moment_k', 'N-mm', 'moment_alt', 'kN-m');
            end
            u = app.Units;
            clr = app.Colors;

            % === 2. CALCULATIONS ===
            T = As * fy;
            a = (As * fy) / (0.85 * fc * b);
            c = a / beta1;
            epsilon_y = fy / Es;
            epsilon_s = epsilon_cu * (d - c) / c;
            
            if epsilon_s >= epsilon_y
                yield_check = true;
                fs = fy;
            else
                yield_check = false;
                fs = epsilon_s * Es;
            end
            
            Mn = As * fs * (d - a/2);
            
            if is_imperial
                Mn_disp = Mn / 12000;
                T_disp = T / 1000;
                Mn_k = Mn / 1000;
            else
                Mn_disp = Mn / 1e6;
                T_disp = T / 1000;
                Mn_k = Mn;
            end

            if is_imperial
                term1 = (3 * sqrt(fc) / fy) * b * d;
                term2 = (200 / fy) * b * d;
            else
                term1 = (0.25 * sqrt(fc) / fy) * b * d;
                term2 = (1.4 / fy) * b * d;
            end
            As_min = max(term1, term2);
            As_check = As >= As_min;
            
            % === 3. CROSS SECTION DIAGRAM ===
            ax = app.AxSection;
            cla(ax); hold(ax, 'on');
            
            % Concrete beam
            rectangle(ax, 'Position', [0, 0, b, h], ...
                'FaceColor', clr.concrete, 'EdgeColor', clr.outline, 'LineWidth', 1.5);
            
            % Compression zone
            patch(ax, [0, b, b, 0], [h, h, h-a, h-a], clr.compression, ...
                'EdgeColor', 'none', 'FaceAlpha', 0.6);
            
            % Neutral axis line
            plot(ax, [0, b], [h-c, h-c], '--', 'Color', clr.neutral, 'LineWidth', 1.2);
            
            % Steel bars
            bar_r = sqrt(bar_A/pi) * 0.7;
            steel_y = h - d;
            if n_bars == 1
                cx = b/2;
            else
                cx = linspace(b*0.12, b*0.88, n_bars);
            end
            for i = 1:n_bars
                rectangle(ax, 'Position', [cx(i)-bar_r, steel_y-bar_r, 2*bar_r, 2*bar_r], ...
                    'FaceColor', clr.steel, 'EdgeColor', [0.1 0.1 0.1], 'Curvature', [1 1], 'LineWidth', 0.5);
            end
            
            % Dimension: h
            xh = b + b*0.08;
            plot(ax, [xh, xh], [0, h], 'k-', 'LineWidth', 0.8);
            plot(ax, [b, xh+b*0.02], [0, 0], 'k-', 'LineWidth', 0.8);
            plot(ax, [b, xh+b*0.02], [h, h], 'k-', 'LineWidth', 0.8);
            text(ax, xh+b*0.04, h/2, sprintf('h=%.1f', h), 'FontSize', 9, 'FontName', 'Arial');
            
            % Dimension: d
            xd = b + b*0.22;
            plot(ax, [xd, xd], [steel_y, h], 'Color', clr.dimension, 'LineWidth', 0.8);
            text(ax, xd+b*0.04, (h+steel_y)/2, sprintf('d=%.1f', d), 'FontSize', 9, 'Color', clr.dimension, 'FontName', 'Arial');
            
            % Dimension: a
            xa = -b*0.08;
            plot(ax, [xa, xa], [h-a, h], 'Color', clr.compression_line, 'LineWidth', 1.5);
            text(ax, xa-b*0.15, h-a/2, sprintf('a=%.2f', a), 'FontSize', 9, 'Color', clr.compression_line, 'FontName', 'Arial');
            
            % Dimension: b
            text(ax, b/2, -h*0.06, sprintf('b=%.1f', b), 'HorizontalAlignment', 'center', 'FontSize', 9, 'FontName', 'Arial');
            
            % c label (neutral axis depth)
            text(ax, b+b*0.04, h-c, sprintf('c=%.2f', c), 'FontSize', 8, 'Color', clr.neutral, 'FontName', 'Arial');
            
            axis(ax, 'equal');
            ax.XLim = [-b*0.25, b*1.4];
            ax.YLim = [-h*0.12, h*1.08];
            ax.XTick = []; ax.YTick = [];
            ax.XColor = 'none'; ax.YColor = 'none';
            title(ax, 'Cross Section', 'FontWeight', 'bold', 'FontSize', 11, 'FontName', 'Arial');
            
            % === 4. STRAIN DIAGRAM ===
            ax = app.AxStrain;
            cla(ax); hold(ax, 'on');
            
            strain_w = 0.4;
            
            % Beam outline (reference)
            plot(ax, [0, 0], [0, h], 'Color', [0.7 0.7 0.7], 'LineWidth', 1);
            
            % Strain profile fill
            x_top = epsilon_cu * strain_w / 0.003;
            x_bot = epsilon_s * strain_w / 0.003;
            patch(ax, [0, x_top, x_bot, 0], [h, h, steel_y, steel_y], clr.strain, ...
                'EdgeColor', clr.strain_edge, 'LineWidth', 1.2, 'FaceAlpha', 0.5);
            
            % Neutral axis
            plot(ax, [-0.05, strain_w*1.2], [h-c, h-c], '--', 'Color', clr.neutral, 'LineWidth', 1);
            text(ax, -0.03, h-c, sprintf('c=%.2f', c), 'FontSize', 8, 'HorizontalAlignment', 'right', 'Color', clr.neutral, 'FontName', 'Arial');
            
            % Labels
            text(ax, x_top+0.02, h, sprintf('ecu=%.4f', epsilon_cu), 'FontSize', 9, 'Color', clr.strain_edge, 'FontName', 'Arial');
            text(ax, x_bot+0.02, steel_y, sprintf('es=%.5f', epsilon_s), 'FontSize', 9, 'Color', clr.strain_edge, 'FontName', 'Arial');
            
            ax.XLim = [-0.1, strain_w*1.5];
            ax.YLim = [-h*0.12, h*1.08];
            ax.XTick = []; ax.YTick = [];
            ax.XColor = 'none'; ax.YColor = 'none';
            title(ax, 'Strain Distribution', 'FontWeight', 'bold', 'FontSize', 11, 'FontName', 'Arial');
            
            % === 5. STRESS/FORCE DIAGRAM ===
            ax = app.AxStress;
            cla(ax); hold(ax, 'on');
            
            stress_w = 0.5;
            
            % Compression block
            patch(ax, [0, stress_w, stress_w, 0], [h, h, h-a, h-a], clr.compression, ...
                'EdgeColor', clr.compression_line, 'LineWidth', 1.2, 'FaceAlpha', 0.7);
            text(ax, stress_w/2, h-a/2, '0.85fc''', 'HorizontalAlignment', 'center', 'FontSize', 9, 'FontName', 'Arial');
            
            % Compression force arrow
            quiver(ax, stress_w+0.05, h-a/2, 0.2, 0, 0, 'Color', clr.compression_line, 'LineWidth', 2, 'MaxHeadSize', 0.8);
            text(ax, stress_w+0.28, h-a/2, sprintf('C=%.0f k', T_disp), 'FontSize', 9, 'Color', clr.compression_line, 'FontName', 'Arial');
            
            % Steel location
            plot(ax, [0, stress_w*0.3], [steel_y, steel_y], 'Color', clr.steel, 'LineWidth', 2);
            
            % Tension force arrow
            quiver(ax, 0, steel_y, 0.25, 0, 0, 'Color', clr.tension, 'LineWidth', 2, 'MaxHeadSize', 0.8);
            text(ax, 0.28, steel_y, sprintf('T=%.0f k', T_disp), 'FontSize', 9, 'Color', clr.tension, 'FontName', 'Arial');
            
            % Neutral axis
            plot(ax, [-0.05, stress_w+0.3], [h-c, h-c], '--', 'Color', clr.neutral, 'LineWidth', 1);
            
            % Moment arm
            xa_arm = stress_w + 0.45;
            plot(ax, [xa_arm, xa_arm], [h-a/2, steel_y], 'Color', clr.moment_arm, 'LineWidth', 1.5);
            plot(ax, [xa_arm-0.02, xa_arm+0.02], [h-a/2, h-a/2], 'Color', clr.moment_arm, 'LineWidth', 1.5);
            plot(ax, [xa_arm-0.02, xa_arm+0.02], [steel_y, steel_y], 'Color', clr.moment_arm, 'LineWidth', 1.5);
            text(ax, xa_arm+0.03, (h-a/2+steel_y)/2, 'd-a/2', 'FontSize', 9, 'Color', clr.moment_arm, 'FontName', 'Arial');
            
            ax.XLim = [-0.1, stress_w+0.65];
            ax.YLim = [-h*0.12, h*1.08];
            ax.XTick = []; ax.YTick = [];
            ax.XColor = 'none'; ax.YColor = 'none';
            title(ax, 'Stress Block & Forces', 'FontWeight', 'bold', 'FontSize', 11, 'FontName', 'Arial');
            
            % === 6. EQUATIONS PANEL ===
            ax = app.AxEquations;
            cla(ax); hold(ax, 'on');
            axis(ax, 'off');
            ax.XLim = [0 1]; ax.YLim = [0 1];
            
            y = 0.92; 
            dy = 0.115;
            fs = 10;
            
            % Header
            text(ax, 0.01, y, 'STEP-BY-STEP CALCULATIONS', 'FontWeight', 'bold', 'FontSize', 12, 'FontName', 'Arial');
            y = y - dy*0.7;
            
            % Step 1
            eq1 = sprintf('$$A_s = n \\times A_{bar} = %.0f \\times %.3f = %.3f \\; \\mathrm{%s}$$', n_bars, bar_A, As, u.area);
            text(ax, 0.01, y, eq1, 'Interpreter', 'latex', 'FontSize', fs);
            y = y - dy*0.6;
            
            eq2 = sprintf('$$T = A_s \\cdot f_y = %.3f \\times %.0f = %.0f \\; \\mathrm{%s} \\;\\; (%.1f \\; \\mathrm{kips})$$', As, fy, T, u.force, T_disp);
            text(ax, 0.01, y, eq2, 'Interpreter', 'latex', 'FontSize', fs);
            y = y - dy;
            
            % Step 2
            eq3 = sprintf('$$a = \\frac{A_s f_y}{0.85 f''_c b} = \\frac{%.0f}{0.85 \\times %.0f \\times %.1f} = %.4f \\; \\mathrm{%s}$$', T, fc, b, a, u.len);
            text(ax, 0.01, y, eq3, 'Interpreter', 'latex', 'FontSize', fs);
            y = y - dy*0.6;
            
            eq4 = sprintf('$$c = \\frac{a}{\\beta_1} = \\frac{%.4f}{%.3f} = %.4f \\; \\mathrm{%s}$$', a, beta1, c, u.len);
            text(ax, 0.01, y, eq4, 'Interpreter', 'latex', 'FontSize', fs);
            y = y - dy;
            
            % Step 3
            eq5 = sprintf('$$\\varepsilon_y = \\frac{f_y}{E_s} = \\frac{%.0f}{%.0f} = %.6f$$', fy, Es, epsilon_y);
            text(ax, 0.01, y, eq5, 'Interpreter', 'latex', 'FontSize', fs);
            
            eq6 = sprintf('$$\\varepsilon_s = \\left(\\frac{d-c}{c}\\right)\\varepsilon_{cu} = \\left(\\frac{%.2f-%.2f}{%.2f}\\right)(%.4f) = %.6f$$', d, c, c, epsilon_cu, epsilon_s);
            text(ax, 0.45, y, eq6, 'Interpreter', 'latex', 'FontSize', fs);
            
            if yield_check
                text(ax, 0.92, y, '[OK]', 'FontSize', 10, 'Color', clr.ok, 'FontWeight', 'bold', 'FontName', 'Arial');
            else
                text(ax, 0.92, y, '[NG]', 'FontSize', 10, 'Color', clr.ng, 'FontWeight', 'bold', 'FontName', 'Arial');
            end
            y = y - dy;
            
            % Step 4
            eq7 = sprintf('$$M_n = A_s f_y \\left(d - \\frac{a}{2}\\right) = %.0f \\left(%.2f - \\frac{%.4f}{2}\\right) = %.0f \\; \\mathrm{%s}$$', T, d, a, Mn_k, u.moment_k);
            text(ax, 0.01, y, eq7, 'Interpreter', 'latex', 'FontSize', fs);
            y = y - dy*0.6;
            
            result_txt = sprintf('Mn = %.1f %s', Mn_disp, u.moment_alt);
            text(ax, 0.01, y, result_txt, 'FontSize', 13, 'Color', clr.result, 'FontWeight', 'bold', 'FontName', 'Arial');
            y = y - dy;
            
            % Step 5
            if is_imperial
                eq9 = sprintf('$$A_{s,min} = \\max\\left(\\frac{3\\sqrt{f''_c}}{f_y}b_wd,\\;\\frac{200}{f_y}b_wd\\right) = %.4f \\; \\mathrm{%s}$$', As_min, u.area);
            else
                eq9 = sprintf('$$A_{s,min} = \\max\\left(\\frac{0.25\\sqrt{f''_c}}{f_y}b_wd,\\;\\frac{1.4}{f_y}b_wd\\right) = %.1f \\; \\mathrm{%s}$$', As_min, u.area);
            end
            text(ax, 0.01, y, eq9, 'Interpreter', 'latex', 'FontSize', fs);
            
            if As_check
                text(ax, 0.75, y, sprintf('As >= As,min [OK]'), 'FontSize', 10, 'Color', clr.ok, 'FontWeight', 'bold', 'FontName', 'Arial');
            else
                text(ax, 0.75, y, sprintf('As < As,min [NG]'), 'FontSize', 10, 'Color', clr.ng, 'FontWeight', 'bold', 'FontName', 'Arial');
            end
            
            % === 7. RESULTS TEXT ===
            if yield_check
                yield_str = 'Yes (Steel Yields)';
            else
                yield_str = 'No (Steel Elastic)';
            end
            
            if As_check
                asmin_str = 'OK';
            else
                asmin_str = 'NOT OK';
            end
            
            results_str = sprintf([...
                'RESULTS SUMMARY\n' ...
                '================\n\n' ...
                'Steel Area:\n' ...
                '  As = %.4f %s\n\n' ...
                'Forces:\n' ...
                '  T = C = %.2f kips\n\n' ...
                'Geometry:\n' ...
                '  a = %.4f %s\n' ...
                '  c = %.4f %s\n\n' ...
                'Strain Check:\n' ...
                '  ey = %.6f\n' ...
                '  es = %.6f\n' ...
                '  Yield: %s\n\n' ...
                'NOMINAL MOMENT:\n' ...
                '  Mn = %.1f %s\n\n' ...
                'Min Steel Check:\n' ...
                '  As,min = %.4f %s\n' ...
                '  Status: %s'], ...
                As, u.area, T_disp, a, u.len, c, u.len, ...
                epsilon_y, epsilon_s, yield_str, ...
                Mn_disp, u.moment_alt, As_min, u.area, asmin_str);
            
            app.ResultsText.Value = results_str;
        end
        
        function switchUnits(app, ~)
            if strcmp(app.UnitSwitch.Value, 'Imperial')
                app.EditFc.Value = 4000;
                app.EditFy.Value = 60000;
                app.EditEs.Value = 29000000;
                app.EditBeta1.Value = 0.85;
                app.EditEpsCu.Value = 0.003;
                app.EditB.Value = 12;
                app.EditH.Value = 20;
                app.EditD.Value = 17.5;
                app.EditBars.Value = 4;
                app.EditBarArea.Value = 0.79;
            else
                app.EditFc.Value = 20;
                app.EditFy.Value = 420;
                app.EditEs.Value = 200000;
                app.EditBeta1.Value = 0.85;
                app.EditEpsCu.Value = 0.003;
                app.EditB.Value = 250;
                app.EditH.Value = 565;
                app.EditD.Value = 500;
                app.EditBars.Value = 3;
                app.EditBarArea.Value = 510;
            end
            updateApp(app);
        end
    end

    methods (Access = public)
        function app = BeamAnalysisApp()
            createComponents(app);
            initializeColors(app);
            updateApp(app);
            registerApp(app, app.UIFigure);
            if nargout == 0
                clear app
            end
        end

        function delete(app)
            delete(app.UIFigure);
        end
    end
    
    methods (Access = private)
        
        function initializeColors(app)
            % Professional color scheme
            app.Colors = struct(...
                'concrete', [0.88 0.88 0.86], ...
                'outline', [0.3 0.3 0.3], ...
                'compression', [0.85 0.55 0.55], ...
                'compression_line', [0.7 0.2 0.2], ...
                'tension', [0.2 0.4 0.7], ...
                'steel', [0.25 0.25 0.3], ...
                'neutral', [0.4 0.4 0.4], ...
                'dimension', [0.2 0.5 0.7], ...
                'strain', [0.7 0.85 0.95], ...
                'strain_edge', [0.2 0.4 0.6], ...
                'moment_arm', [0.2 0.6 0.3], ...
                'result', [0.1 0.3 0.6], ...
                'ok', [0.1 0.5 0.2], ...
                'ng', [0.7 0.15 0.15], ...
                'bg', [0.97 0.97 0.97], ...
                'panel_bg', [1 1 1]);
        end
        
        function createComponents(app)
            % === MAIN FIGURE ===
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [80 60 1400 800];
            app.UIFigure.Name = 'Beam Analysis - Nominal Moment Strength (ACI 318)';
            app.UIFigure.Color = [0.94 0.94 0.94];
            app.UIFigure.Resize = 'on';

            % === MAIN GRID ===
            app.MainGrid = uigridlayout(app.UIFigure);
            app.MainGrid.ColumnWidth = {'0.18x', '0.82x'};
            app.MainGrid.RowHeight = {'1x'};
            app.MainGrid.Padding = [8 8 8 8];
            app.MainGrid.ColumnSpacing = 8;

            % === LEFT: INPUT PANEL ===
            app.InputPanel = uipanel(app.MainGrid);
            app.InputPanel.Layout.Row = 1;
            app.InputPanel.Layout.Column = 1;
            app.InputPanel.Title = 'INPUT PARAMETERS';
            app.InputPanel.FontWeight = 'bold';
            app.InputPanel.FontSize = 11;
            app.InputPanel.BackgroundColor = [1 1 1];

            inpGrid = uigridlayout(app.InputPanel);
            inpGrid.ColumnWidth = {'1.3x', '1x'};
            inpGrid.RowHeight = repmat({'fit'}, 1, 16);
            inpGrid.RowSpacing = 4;
            inpGrid.Padding = [8 8 8 8];
            
            % Unit Switch
            lbl = uilabel(inpGrid); lbl.Text = 'Unit System'; lbl.FontWeight = 'bold';
            app.UnitSwitch = uiswitch(inpGrid, 'slider');
            app.UnitSwitch.Items = {'Imperial', 'SI'};
            app.UnitSwitch.ValueChangedFcn = createCallbackFcn(app, @switchUnits, true);
            
            % Separator - Materials
            lbl = uilabel(inpGrid); lbl.Text = 'MATERIALS'; lbl.FontWeight = 'bold'; lbl.FontColor = [0.3 0.3 0.5];
            uilabel(inpGrid);
            
            % fc
            lbl = uilabel(inpGrid); lbl.Text = 'fc'' (Concrete)';
            app.EditFc = uieditfield(inpGrid, 'numeric');
            app.EditFc.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % fy
            lbl = uilabel(inpGrid); lbl.Text = 'fy (Steel Yield)';
            app.EditFy = uieditfield(inpGrid, 'numeric');
            app.EditFy.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % Es
            lbl = uilabel(inpGrid); lbl.Text = 'Es (Modulus)';
            app.EditEs = uieditfield(inpGrid, 'numeric');
            app.EditEs.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % beta1
            lbl = uilabel(inpGrid); lbl.Text = 'Beta1';
            app.EditBeta1 = uieditfield(inpGrid, 'numeric');
            app.EditBeta1.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % epsilon_cu
            lbl = uilabel(inpGrid); lbl.Text = 'ecu (Ult. Strain)';
            app.EditEpsCu = uieditfield(inpGrid, 'numeric');
            app.EditEpsCu.ValueDisplayFormat = '%.4f';
            app.EditEpsCu.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % Separator - Geometry
            lbl = uilabel(inpGrid); lbl.Text = 'GEOMETRY'; lbl.FontWeight = 'bold'; lbl.FontColor = [0.3 0.3 0.5];
            uilabel(inpGrid);
            
            % b
            lbl = uilabel(inpGrid); lbl.Text = 'b (Width)';
            app.EditB = uieditfield(inpGrid, 'numeric');
            app.EditB.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % h
            lbl = uilabel(inpGrid); lbl.Text = 'h (Total Depth)';
            app.EditH = uieditfield(inpGrid, 'numeric');
            app.EditH.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % d
            lbl = uilabel(inpGrid); lbl.Text = 'd (Eff. Depth)';
            app.EditD = uieditfield(inpGrid, 'numeric');
            app.EditD.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % Separator - Reinforcement
            lbl = uilabel(inpGrid); lbl.Text = 'REINFORCEMENT'; lbl.FontWeight = 'bold'; lbl.FontColor = [0.3 0.3 0.5];
            uilabel(inpGrid);
            
            % Bars
            lbl = uilabel(inpGrid); lbl.Text = 'Number of Bars';
            app.EditBars = uieditfield(inpGrid, 'numeric');
            app.EditBars.ValueDisplayFormat = '%.0f';
            app.EditBars.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);
            
            % Bar Area
            lbl = uilabel(inpGrid); lbl.Text = 'Bar Area (each)';
            app.EditBarArea = uieditfield(inpGrid, 'numeric');
            app.EditBarArea.ValueChangedFcn = createCallbackFcn(app, @updateApp, true);

            % === RIGHT PANEL ===
            rightGrid = uigridlayout(app.MainGrid);
            rightGrid.Layout.Row = 1;
            rightGrid.Layout.Column = 2;
            rightGrid.ColumnWidth = {'1x', '1x', '1x', '0.6x'};
            rightGrid.RowHeight = {'1.2x', '1.5x'};
            rightGrid.Padding = [0 0 0 0];
            rightGrid.ColumnSpacing = 6;
            rightGrid.RowSpacing = 6;

            % --- Diagram Panels ---
            % Section
            sectionPanel = uipanel(rightGrid);
            sectionPanel.Layout.Row = 1;
            sectionPanel.Layout.Column = 1;
            sectionPanel.BackgroundColor = [1 1 1];
            sectionPanel.BorderType = 'line';
            
            secGrid = uigridlayout(sectionPanel);
            secGrid.ColumnWidth = {'1x'};
            secGrid.RowHeight = {'1x'};
            secGrid.Padding = [2 2 2 2];
            
            app.AxSection = uiaxes(secGrid);
            app.AxSection.Layout.Row = 1;
            app.AxSection.Layout.Column = 1;
            
            % Strain
            strainPanel = uipanel(rightGrid);
            strainPanel.Layout.Row = 1;
            strainPanel.Layout.Column = 2;
            strainPanel.BackgroundColor = [1 1 1];
            strainPanel.BorderType = 'line';
            
            strGrid = uigridlayout(strainPanel);
            strGrid.ColumnWidth = {'1x'};
            strGrid.RowHeight = {'1x'};
            strGrid.Padding = [2 2 2 2];
            
            app.AxStrain = uiaxes(strGrid);
            app.AxStrain.Layout.Row = 1;
            app.AxStrain.Layout.Column = 1;
            
            % Stress
            stressPanel = uipanel(rightGrid);
            stressPanel.Layout.Row = 1;
            stressPanel.Layout.Column = 3;
            stressPanel.BackgroundColor = [1 1 1];
            stressPanel.BorderType = 'line';
            
            stressGrid = uigridlayout(stressPanel);
            stressGrid.ColumnWidth = {'1x'};
            stressGrid.RowHeight = {'1x'};
            stressGrid.Padding = [2 2 2 2];
            
            app.AxStress = uiaxes(stressGrid);
            app.AxStress.Layout.Row = 1;
            app.AxStress.Layout.Column = 1;
            
            % Results
            app.ResultsPanel = uipanel(rightGrid);
            app.ResultsPanel.Layout.Row = 1;
            app.ResultsPanel.Layout.Column = 4;
            app.ResultsPanel.Title = 'Results';
            app.ResultsPanel.FontWeight = 'bold';
            app.ResultsPanel.BackgroundColor = [0.98 0.98 0.95];
            
            resGrid = uigridlayout(app.ResultsPanel);
            resGrid.ColumnWidth = {'1x'};
            resGrid.RowHeight = {'1x'};
            resGrid.Padding = [4 4 4 4];
            
            app.ResultsText = uitextarea(resGrid);
            app.ResultsText.Layout.Row = 1;
            app.ResultsText.Layout.Column = 1;
            app.ResultsText.FontName = 'Consolas';
            app.ResultsText.FontSize = 9;
            app.ResultsText.Editable = 'off';
            app.ResultsText.BackgroundColor = [0.98 0.98 0.95];
            
            % --- Equations Panel ---
            app.EquationsPanel = uipanel(rightGrid);
            app.EquationsPanel.Layout.Row = 2;
            app.EquationsPanel.Layout.Column = [1 4];
            app.EquationsPanel.Title = 'Calculation Procedure (ACI 318)';
            app.EquationsPanel.FontWeight = 'bold';
            app.EquationsPanel.BackgroundColor = [1 1 1];
            
            eqGrid = uigridlayout(app.EquationsPanel);
            eqGrid.ColumnWidth = {'1x'};
            eqGrid.RowHeight = {'1x'};
            eqGrid.Padding = [4 4 4 4];
            
            app.AxEquations = uiaxes(eqGrid);
            app.AxEquations.Layout.Row = 1;
            app.AxEquations.Layout.Column = 1;
            app.AxEquations.XTick = [];
            app.AxEquations.YTick = [];
            app.AxEquations.XColor = 'none';
            app.AxEquations.YColor = 'none';

            % === SET INITIAL VALUES ===
            app.EditFc.Value = 4000;
            app.EditFy.Value = 60000;
            app.EditEs.Value = 29000000;
            app.EditBeta1.Value = 0.85;
            app.EditEpsCu.Value = 0.003;
            app.EditB.Value = 12;
            app.EditH.Value = 20;
            app.EditD.Value = 17.5;
            app.EditBars.Value = 4;
            app.EditBarArea.Value = 0.79;

            app.UIFigure.Visible = 'on';
        end
    end
end

