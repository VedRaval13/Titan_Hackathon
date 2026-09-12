from ortools.sat.python import cp_model


class WorkloadOptimizer:
    MAX_WORKLOAD = 8.0

    def optimize(self, tasks: list[dict], employees: list[dict]) -> dict:
        if not tasks or not employees:
            return {
                "status": "no_data",
                "assignment_map": {},
                "workload_distribution": {},
                "solver_status": "NO_DATA",
            }

        model = cp_model.CpModel()
        SCALE = 100

        x = {}
        for t in tasks:
            for e in employees:
                x[(t["id"], e["id"])] = model.new_bool_var(f'x_{t["id"]}_{e["id"]}')

        # Constraint 1: Each task assigned to exactly one employee
        for t in tasks:
            model.add_exactly_one(x[(t["id"], e["id"])] for e in employees)

        # Constraints 2 & 3: Skill match and availability
        for t in tasks:
            req_skills = {s.lower() for s in t.get("required_skills", [])}
            for e in employees:
                emp_skills = {s.lower() for s in e.get("skills", [])}

                if e.get("availability_status", "").lower() == "unavailable":
                    model.add(x[(t["id"], e["id"])] == 0)
                    continue

                if req_skills and not req_skills.intersection(emp_skills):
                    model.add(x[(t["id"], e["id"])] == 0)

        # Constraint 4: Workload cap + objective
        max_load = model.new_int_var(0, 10000, "max_load")

        for e in employees:
            current_w = int(e.get("current_workload_score", 0.0) * SCALE)

            # Build list of (coefficient, variable) for employee task loads
            task_load_terms = []
            for t in tasks:
                est_hrs = int(t.get("estimated_hours", 4.0) * SCALE)
                task_load_terms.append((est_hrs, x[(t["id"], e["id"])]))

            # total_employee_load = current_w + sum(est_hrs * x[t,e] for all t)
            # Use model.add with weighted sum
            total_load = model.new_int_var(0, 10000, f"load_{e['id']}")
            model.add(
                total_load
                == current_w
                + sum(coeff * var for coeff, var in task_load_terms)
            )

            model.add(total_load <= int(self.MAX_WORKLOAD * SCALE))
            model.add(total_load <= max_load)

        model.minimize(max_load)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            assignment_map = {}
            workload_dist = {}
            for e in employees:
                workload_dist[e["id"]] = e.get("current_workload_score", 0.0)

            for t in tasks:
                for e in employees:
                    if solver.value(x[(t["id"], e["id"])]) == 1:
                        assignment_map[t["id"]] = e["id"]
                        workload_dist[e["id"]] += t.get("estimated_hours", 4.0)

            return {
                "status": "optimal" if status == cp_model.OPTIMAL else "feasible",
                "assignment_map": assignment_map,
                "workload_distribution": workload_dist,
                "solver_status": solver.status_name(status),
            }
        else:
            return self._relaxed_optimize(tasks, employees)

    def _relaxed_optimize(self, tasks: list[dict], employees: list[dict]) -> dict:
        model = cp_model.CpModel()
        SCALE = 100
        RELAXED_MAX = 10.0

        x = {}
        for t in tasks:
            for e in employees:
                x[(t["id"], e["id"])] = model.new_bool_var(f'x_{t["id"]}_{e["id"]}')

        for t in tasks:
            model.add_exactly_one(x[(t["id"], e["id"])] for e in employees)

        for t in tasks:
            req_skills = {s.lower() for s in t.get("required_skills", [])}
            for e in employees:
                emp_skills = {s.lower() for s in e.get("skills", [])}
                if e.get("availability_status", "").lower() == "unavailable":
                    model.add(x[(t["id"], e["id"])] == 0)
                    continue
                if req_skills and not req_skills.intersection(emp_skills):
                    model.add(x[(t["id"], e["id"])] == 0)

        max_load = model.new_int_var(0, 10000, "max_load")

        for e in employees:
            current_w = int(e.get("current_workload_score", 0.0) * SCALE)
            task_load_terms = []
            for t in tasks:
                est_hrs = int(t.get("estimated_hours", 4.0) * SCALE)
                task_load_terms.append((est_hrs, x[(t["id"], e["id"])]))

            total_load = model.new_int_var(0, 10000, f"load_{e['id']}")
            model.add(
                total_load
                == current_w
                + sum(coeff * var for coeff, var in task_load_terms)
            )
            model.add(total_load <= int(RELAXED_MAX * SCALE))
            model.add(total_load <= max_load)

        model.minimize(max_load)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            assignment_map = {}
            workload_dist = {}
            for e in employees:
                workload_dist[e["id"]] = e.get("current_workload_score", 0.0)

            for t in tasks:
                for e in employees:
                    if solver.value(x[(t["id"], e["id"])]) == 1:
                        assignment_map[t["id"]] = e["id"]
                        workload_dist[e["id"]] += t.get("estimated_hours", 4.0)

            return {
                "status": "feasible_relaxed",
                "warning": f"Workload constraint relaxed from {self.MAX_WORKLOAD} to {RELAXED_MAX} to find a feasible solution.",
                "assignment_map": assignment_map,
                "workload_distribution": workload_dist,
                "solver_status": solver.status_name(status),
            }

        return {
            "status": "infeasible",
            "warning": "No feasible assignment found even with relaxed constraints.",
            "assignment_map": {},
            "workload_distribution": {},
        }

    def preview(self, tasks: list[dict], employees: list[dict]) -> dict:
        before = {e["id"]: e.get("current_workload_score", 0.0) for e in employees}
        result = self.optimize(tasks, employees)
        after = result.get("workload_distribution", {})
        result["before_workload"] = before
        result["after_workload"] = after
        return result
